import { spawn } from "node:child_process";
import { watch } from "node:fs";
import { readdir, stat } from "node:fs/promises";
import path from "node:path";

const ROOT = process.cwd();
const NOTES_DIR = path.join(ROOT, "docs", "src", "Notes");
const VITEPRESS_BIN = path.join(
  ROOT,
  "node_modules",
  "vitepress",
  "bin",
  "vitepress.js"
);

async function collectDirs(dir, baseDir = dir, out = new Set()) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const ent of entries) {
    if (ent.name.startsWith(".")) continue;
    const abs = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      const rel = path.relative(baseDir, abs).split(path.sep).join("/");
      out.add(rel);
      await collectDirs(abs, baseDir, out);
    }
  }
  return out;
}

async function collectMdFiles(dir, baseDir = dir, out = new Set()) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const ent of entries) {
    // ignore dot dirs/files
    if (ent.name.startsWith(".")) continue;

    const abs = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      await collectMdFiles(abs, baseDir, out);
      continue;
    }
    if (ent.isFile() && ent.name.endsWith(".md")) {
      const rel = path.relative(baseDir, abs).split(path.sep).join("/");
      out.add(rel);
    }
  }
  return out;
}

function parseArgs(argv) {
  const args = new Set(argv.slice(2));
  return {
    check: args.has("--check"),
  };
}

let child = null;
let restarting = false;
let restartTimer = null;

function startDev() {
  child = spawn(process.execPath, [VITEPRESS_BIN, "dev", "docs"], {
    stdio: "inherit",
    env: process.env,
  });
}

async function stopDev() {
  if (!child) return;
  const p = child;
  child = null;

  if (p.exitCode !== null) return;

  await new Promise((resolve) => {
    const killTimer = setTimeout(() => {
      try {
        p.kill("SIGKILL");
      } catch {
        // ignore
      }
    }, 1500);

    p.once("exit", () => {
      clearTimeout(killTimer);
      resolve();
    });

    try {
      p.kill("SIGTERM");
    } catch {
      clearTimeout(killTimer);
      resolve();
    }
  });
}

function scheduleRestart(reason, file) {
  if (restartTimer) clearTimeout(restartTimer);
  restartTimer = setTimeout(async () => {
    if (restarting) return;
    restarting = true;
    console.log(
      `[docs:dev] Notes 目录发生 ${reason}：${file}，正在重启以刷新 sidebar...`
    );
    try {
      await stopDev();
      startDev();
    } finally {
      restarting = false;
    }
  }, 150);
}

async function fileExists(absPath) {
  try {
    await stat(absPath);
    return true;
  } catch {
    return false;
  }
}

async function statSafe(absPath) {
  try {
    return await stat(absPath);
  } catch {
    return null;
  }
}

async function main() {
  const { check } = parseArgs(process.argv);

  const mdSet = await collectMdFiles(NOTES_DIR);
  const dirSet = await collectDirs(NOTES_DIR);

  if (check) {
    console.log(
      `[docs:dev] --check OK: ${mdSet.size} 个 md 文件（扫描目录：${NOTES_DIR}）`
    );
    return;
  }

  // 启动 dev server
  startDev();

  // 监听 Notes 目录：只在新增/删除 md 文件时重启
  // 注意：macOS 支持 recursive；若未来迁移到不支持的平台，可换 chokidar。
  watch(NOTES_DIR, { recursive: true }, async (eventType, filename) => {
    if (!filename) return;
    if (eventType !== "rename") return;

    const rel = filename.split(path.sep).join("/");
    const abs = path.join(NOTES_DIR, filename);

    // md 新增/删除
    if (rel.endsWith(".md")) {
      const exists = await fileExists(abs);
      if (exists && !mdSet.has(rel)) {
        mdSet.add(rel);
        scheduleRestart("新增", rel);
      } else if (!exists && mdSet.has(rel)) {
        mdSet.delete(rel);
        scheduleRestart("删除", rel);
      }
      return;
    }

    // 目录新增/删除（用于让 sidebar 分组立即刷新）
    const st = await statSafe(abs);
    if (st?.isDirectory() && !dirSet.has(rel)) {
      dirSet.add(rel);
      scheduleRestart("新增目录", rel);
      return;
    }
    if (!st && dirSet.has(rel)) {
      dirSet.delete(rel);
      scheduleRestart("删除目录", rel);
    }
  });

  const shutdown = async () => {
    try {
      await stopDev();
    } finally {
      process.exit(0);
    }
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((err) => {
  console.error("[docs:dev] watcher 启动失败：", err);
  process.exit(1);
});


