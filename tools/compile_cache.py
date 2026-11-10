import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time


class ArtifactCache:
    def __init__(self, directory, run):
        self.directory = Path(directory).resolve()
        self.run_command = run
        self.hits = 0
        self.misses = 0
        self.hashes = {}

    def file_hash(self, path):
        stat = path.stat()
        stamp = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)
        previous = self.hashes.get(path)
        if previous is None or previous[0] != stamp:
            value = hashlib.sha256()
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    value.update(block)
            self.hashes[path] = (stamp, value.hexdigest())
        return self.hashes[path][1]

    def run(self, command, timeout=180):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return self.compile(command, timeout)


class SangokuCache(ArtifactCache):
    def __init__(self, directory, sangoku, run):
        super().__init__(directory, run)
        self.sangoku = Path(sangoku).resolve()
        self.repo = next(
            (
                p
                for p in self.sangoku.parents
                if (p / "src/main.rs").is_file() and (p / "Cargo.toml").is_file()
            ),
            None,
        )
        if self.repo is None:
            with self.sangoku.open("rb") as binary:
                binary.seek(-16, 2)
                if binary.read() != b"SANGOKU-BUNDLE1!":
                    raise ValueError("cannot locate Sangoku sources; use --no-cache")
        self.inputs = self.compiler_inputs()

    def compiler_inputs(self):
        inputs = {}
        if self.repo:
            for directory, paths in [
                (
                    self.repo,
                    ["src", "runtime", "targets", "Cargo.toml", "Cargo.lock", ".cargo"],
                ),
                (self.repo / "third_party/rustc_codegen_cranelift", ["."]),
                (
                    self.repo / "third_party/wasmtime",
                    ["cranelift", "crates", "Cargo.toml", "Cargo.lock", ".cargo"],
                ),
                (self.repo / "third_party/rust", ["library"]),
            ]:
                result = self.run_command(
                    [
                        "git",
                        "ls-files",
                        "-z",
                        "--cached",
                        "--others",
                        "--exclude-standard",
                        "--",
                        *paths,
                    ],
                    cwd=directory,
                )
                if result["returncode"] != 0:
                    raise ValueError(f"cannot fingerprint {directory}; use --no-cache")
                for name in sorted(set(result["stdout"].split("\0")) - {""}):
                    path = directory / name
                    if path.is_file():
                        inputs[str(path)] = self.file_hash(path)
            outcome = self.run_command(["rustc", "+gbc-lr35902", "--print", "sysroot"])
            if outcome["returncode"] != 0:
                raise ValueError("cannot fingerprint Rust toolchain; use --no-cache")
            sysroot = Path(outcome["stdout"].strip())
            for path in [
                sysroot / "bin/rustc",
                *sorted((sysroot / "lib").glob("*rustc_driver*")),
            ]:
                inputs[str(path)] = self.file_hash(path)
        for tool in ["rgbasm", "rgblink", "rgbfix"]:
            executable = shutil.which(tool)
            if executable:
                path = Path(executable).resolve()
                inputs[str(path)] = self.file_hash(path)
        inputs["environment"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("RUST", "CARGO", "CG_", "SANGOKU"))
            or key in {"PATH", "LD_LIBRARY_PATH"}
        }
        return inputs

    def key(self, command):
        inputs = dict(self.inputs)
        inputs[str(self.sangoku)] = self.file_hash(self.sangoku)
        if self.repo:
            backend = (
                self.repo
                / "third_party/rustc_codegen_cranelift/target/release/librustc_codegen_cranelift.so"
            )
            inputs[str(backend)] = (
                self.file_hash(backend) if backend.is_file() else None
            )
        payload = [
            1,
            inputs,
            command[1],
            Path(command[2]).name,
            self.file_hash(Path(command[2])),
            [str(arg) for arg in command[4:]],
        ]
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def compile(self, command, timeout):
        key = self.key(command)
        entry = self.directory / key
        metadata = entry / "result.json"
        try:
            saved = json.loads(metadata.read_text())
            if not all(
                (entry / name).is_file() and self.file_hash(entry / name) == digest
                for name, digest in saved["files"].items()
            ):
                raise ValueError("cached artifact missing or changed")
            shutil.copyfile(entry / "output", command[3])
            self.hits += 1
            return {
                **saved["result"],
                "command": [str(arg) for arg in command],
                "cache_hit": True,
            }
        except (OSError, ValueError, KeyError):
            pass
        self.misses += 1
        staging = Path(tempfile.mkdtemp(prefix=".compile-", dir=self.directory))
        source = staging / Path(command[2]).name
        shutil.copyfile(command[2], source)
        cached_command = [
            command[0],
            command[1],
            source,
            staging / "output",
            *command[4:],
        ]
        result = self.run_command(cached_command, cwd=staging, timeout=timeout)
        if result["returncode"] != 0 or not (staging / "output").is_file():
            shutil.rmtree(staging)
            return {**result, "cache_hit": False}
        # the backend may have been rebuilt by this invocation.
        key = self.key(command)
        entry = self.directory / key
        if entry.exists():
            shutil.rmtree(entry)
        staging.rename(entry)
        result = {
            **result,
            "command": [str(arg) for arg in command],
            "stdout": result["stdout"].replace(str(staging), str(entry)),
            "stderr": result["stderr"].replace(str(staging), str(entry)),
        }
        files = {
            str(path.relative_to(entry)): self.file_hash(path)
            for path in sorted(entry.rglob("*"))
            if path.is_file()
        }
        metadata = entry / "result.json"
        metadata.write_text(json.dumps({"result": result, "files": files}) + "\n")
        shutil.copyfile(entry / "output", command[3])
        return {**result, "cache_hit": False}


class SdccCache(ArtifactCache):
    def __init__(self, directory, sdcc, run):
        super().__init__(directory, run)
        self.sdcc = Path(shutil.which(str(sdcc)) or sdcc).resolve()
        self.seconds = 0.0
        self.inputs = {}
        search = run([self.sdcc, "-msm83", "--print-search-dirs"])
        if search["returncode"] != 0:
            raise ValueError("cannot fingerprint SDCC installation; use --no-cache")
        section = None
        directories = set()
        programs = []
        for line in search["stdout"].splitlines():
            if line.endswith(":"):
                section = line
            elif line:
                if section in {"includedir:", "libdir:", "libpath:"}:
                    directories.add(Path(line).resolve())
                elif section == "programs:":
                    programs.append(line)
        for directory in sorted(directories):
            if directory.is_dir():
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        self.inputs[str(path)] = self.file_hash(path)
        for name in ["sdcc", "sdcpp", "sdasgb", "sdldgb", "sdld"]:
            executable = (
                self.sdcc
                if name == "sdcc"
                else shutil.which(name, path=os.pathsep.join(programs))
            )
            if executable:
                path = Path(executable).resolve()
                self.inputs[str(path)] = self.file_hash(path)
        self.inputs["environment"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("SDCC") or key in {"PATH", "LD_LIBRARY_PATH"}
        }
        self.input_hash = hashlib.sha256(
            json.dumps(self.inputs, sort_keys=True).encode()
        ).hexdigest()

    def compile(self, command, timeout):
        command = [str(arg) for arg in command]
        output_index = command.index("-o") + 1
        output = Path(command[output_index])
        source_index = next(
            i
            for i, arg in enumerate(command[1:], 1)
            if Path(arg).suffix in {".c", ".rel"}
        )
        source = Path(command[source_index])
        normalized = command.copy()
        normalized[0] = str(self.sdcc)
        normalized[source_index] = [source.name, self.file_hash(source)]
        normalized[output_index] = output.name
        payload = [2, self.input_hash, normalized]
        key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        entry = self.directory / key
        companions = {".rel": [".asm"], ".ihx": [".map"]}.get(output.suffix, [])
        outputs = [output, *(output.with_suffix(suffix) for suffix in companions)]
        try:
            saved = json.loads((entry / "result.json").read_text())
            if set(saved["files"]) != {path.name for path in outputs}:
                raise ValueError("cached artifacts are incomplete")
            if not all(
                (entry / name).is_file() and self.file_hash(entry / name) == digest
                for name, digest in saved["files"].items()
            ):
                raise ValueError("cached artifact missing or changed")
            for name in saved["files"]:
                shutil.copyfile(entry / name, output.parent / name)
            self.hits += 1
            result = {**saved["result"], "command": command, "cache_hit": True}
            for stream in ("stdout", "stderr"):
                for index in (source_index, output_index):
                    result[stream] = result[stream].replace(
                        saved["result"]["command"][index], command[index]
                    )
            return result
        except (OSError, ValueError, KeyError):
            pass
        self.misses += 1
        started = time.monotonic()
        result = self.run_command(command, timeout=timeout)
        elapsed = time.monotonic() - started
        self.seconds += elapsed
        if result["returncode"] != 0 or not all(path.is_file() for path in outputs):
            return {**result, "cache_hit": False, "elapsed_seconds": elapsed}
        staging = Path(tempfile.mkdtemp(prefix=".compile-", dir=self.directory))
        files = {}
        for path in outputs:
            shutil.copyfile(path, staging / path.name)
            files[path.name] = self.file_hash(staging / path.name)
        saved = {"result": {**result, "elapsed_seconds": elapsed}, "files": files}
        (staging / "result.json").write_text(json.dumps(saved) + "\n")
        if entry.exists():
            shutil.rmtree(entry)
        staging.rename(entry)
        return {**saved["result"], "cache_hit": False}
