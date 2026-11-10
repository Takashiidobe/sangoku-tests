import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
compile_cache = importlib.import_module("compile_cache")
SangokuCache = compile_cache.SangokuCache
SdccCache = compile_cache.SdccCache


class CompileCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.driver = self.work / "sangoku"
        self.driver.write_bytes(b"SANGOKU-BUNDLE1!")
        self.source = self.work / "case.rs"
        self.source.write_text("fn probe() {}")
        self.output = self.work / "case.asm"
        self.calls = []
        self.fail = False
        self.backend = None
        self.cache = self.new_cache()

    def new_cache(self):
        with patch.object(
            SangokuCache, "compiler_inputs", return_value={"runtime": "v1"}
        ):
            return SangokuCache(self.work / "cache", self.driver, self.run_compiler)

    def command(self, phase="asm", opt="z"):
        return [self.driver, phase, self.source, self.output, "--opt-level", opt]

    def run_compiler(self, command, cwd, timeout):
        self.calls.append(command)
        if self.fail:
            return {
                "command": list(map(str, command)),
                "returncode": 1,
                "stdout": "",
                "stderr": "failed",
            }
        if self.backend:
            self.backend.write_text("rebuilt")
        Path(command[3]).write_text("ret")
        artifacts = cwd / "build/artifacts/probe"
        artifacts.mkdir(parents=True)
        (artifacts / "probe.map").write_text("map")
        (artifacts / "probe.asm").write_text("assembly")
        return {
            "command": list(map(str, command)),
            "returncode": 0,
            "stdout": "",
            "stderr": f"Build artifacts: {artifacts}\n",
        }

    def test_reuses_across_runs_and_restores_output_and_artifacts(self):
        first = self.cache.run(self.command("build"))
        self.output.unlink()
        cache = self.new_cache()
        second = cache.run(self.command("build"))
        self.assertFalse(first["cache_hit"])
        self.assertTrue(second["cache_hit"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.output.read_text(), "ret")
        artifacts = Path(second["stderr"].split("Build artifacts: ")[1].strip())
        self.assertEqual((artifacts / "probe.map").read_text(), "map")
        self.assertEqual((artifacts / "probe.asm").read_text(), "assembly")

    def test_source_driver_runtime_mode_and_phase_invalidate(self):
        self.cache.run(self.command())
        self.source.write_text("fn changed() {}")
        self.assertFalse(self.cache.run(self.command())["cache_hit"])
        self.driver.write_bytes(b"changed SANGOKU-BUNDLE1!")
        self.assertFalse(self.cache.run(self.command())["cache_hit"])
        self.cache.inputs["runtime"] = "v2"
        self.assertFalse(self.cache.run(self.command())["cache_hit"])
        self.assertFalse(self.cache.run(self.command(opt="3"))["cache_hit"])
        self.assertFalse(self.cache.run(self.command("build"))["cache_hit"])
        self.assertEqual(len(self.calls), 6)

    def test_failures_are_retried(self):
        self.fail = True
        for _ in range(2):
            self.assertEqual(self.cache.run(self.command())["returncode"], 1)
        self.assertEqual(len(self.calls), 2)
        self.assertFalse(list(self.cache.directory.glob("*/result.json")))

    def test_missing_or_corrupt_artifacts_are_rebuilt(self):
        self.cache.run(self.command("build"))
        artifact = next(self.cache.directory.glob("*/build/artifacts/probe/probe.map"))
        artifact.write_text("corrupt")
        self.assertFalse(self.cache.run(self.command("build"))["cache_hit"])
        artifact.unlink()
        self.assertFalse(self.cache.run(self.command("build"))["cache_hit"])
        self.assertEqual(len(self.calls), 3)

    def test_dirty_compiler_sources_and_toolchain_invalidate_across_runs(self):
        repo = self.work / "checkout"
        driver = repo / "target/release/sangoku"
        driver.parent.mkdir(parents=True)
        driver.write_bytes(b"driver")
        files = [
            repo / "src/main.rs",
            repo / "runtime/memcpy.asm",
            repo / "third_party/rustc_codegen_cranelift/src/lib.rs",
            repo / "third_party/wasmtime/cranelift/codegen/src/lib.rs",
            repo / "third_party/rust/library/core/src/lib.rs",
        ]
        (repo / "Cargo.toml").write_text("manifest")
        rustc = self.work / "toolchain/bin/rustc"
        for path in [*files, rustc]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("initial")

        def runner(command, cwd=None, **kwargs):
            if command[0] == "git":
                names = [
                    str(path.relative_to(cwd))
                    for path in files
                    if path.is_relative_to(cwd)
                ]
                return {"returncode": 0, "stdout": "\0".join(names)}
            if command[0] == "rustc":
                return {"returncode": 0, "stdout": str(rustc.parent.parent)}
            return self.run_compiler(command, cwd=cwd, **kwargs)

        def build():
            with patch("compile_cache.shutil.which", return_value=None):
                cache = SangokuCache(self.work / "cache", driver, runner)
            return cache.run([driver, *self.command()[1:]])

        self.assertFalse(build()["cache_hit"])
        self.assertTrue(build()["cache_hit"])
        for path in [*files, rustc]:
            path.write_text("changed")
            self.assertFalse(build()["cache_hit"], str(path))
            self.assertTrue(build()["cache_hit"], str(path))

    def test_backend_rebuild_is_saved_under_updated_fingerprint(self):
        self.cache.repo = self.work
        self.backend = (
            self.work
            / "third_party/rustc_codegen_cranelift/target/release/librustc_codegen_cranelift.so"
        )
        self.backend.parent.mkdir(parents=True)
        self.cache.run(self.command())
        self.assertTrue(self.cache.run(self.command())["cache_hit"])
        self.backend.write_text("external rebuild")
        self.assertFalse(self.cache.run(self.command())["cache_hit"])
        saved = json.loads(next(self.cache.directory.glob("*/result.json")).read_text())
        self.assertIn("output", saved["files"])


class SdccCacheTests(unittest.TestCase):
    def test_reuses_compile_and_link_outputs_and_invalidates_library_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            driver = work / "sdcc"
            driver.write_bytes(b"sdcc")
            library = work / "lib/sm83.lib"
            library.parent.mkdir()
            library.write_bytes(b"library")
            header = work / "include/stdint.h"
            header.parent.mkdir()
            header.write_text("typedef unsigned char uint8_t;")
            calls = []

            def runner(command, timeout=180):
                if "--print-search-dirs" in command:
                    return {
                        "returncode": 0,
                        "stdout": f"includedir:\n{header.parent}\nlibdir:\n{library.parent}\n",
                    }
                calls.append(command)
                output = Path(command[-1])
                output.write_bytes(b"output")
                output.with_suffix(
                    ".asm" if output.suffix == ".rel" else ".map"
                ).write_bytes(b"companion")
                return {"returncode": 0, "command": command, "stdout": "", "stderr": ""}

            def build(name):
                cache = SdccCache(work / "cache", driver, runner)
                directory = work / name
                directory.mkdir()
                source = directory / "fixture.c"
                source.write_text("uint8_t probe(void) { return 0; }")
                rel = directory / "output.rel"
                ihx = directory / "output.ihx"
                compile_result = cache.run([driver, "-c", source, "-o", rel])
                link_result = cache.run([driver, rel, "-o", ihx])
                for suffix, content in [
                    (".rel", b"output"),
                    (".ihx", b"output"),
                    (".asm", b"companion"),
                    (".map", b"companion"),
                ]:
                    self.assertEqual(rel.with_suffix(suffix).read_bytes(), content)
                return [result["cache_hit"] for result in (compile_result, link_result)]

            self.assertEqual(build("first"), [False, False])
            self.assertEqual(build("repeat"), [True, True])
            library.write_bytes(b"changed library")
            self.assertEqual(build("library-change"), [False, False])
            header.write_text("typedef unsigned int uint8_t;")
            self.assertEqual(build("header-change"), [False, False])
            self.assertEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main()
