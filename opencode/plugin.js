import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Plugin, Skill } from "@opencode/plugin";

const name = "browsercontrol";
const root = fileURLToPath(new URL("../", import.meta.url));
const skillPath = join(root, "skills", name, "SKILL.md");

export default Plugin.define({
  id: name,
  async setup(ctx) {
    const source = await readFile(skillPath, "utf8");
    const content = source.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "").trim();
    const directoryHash = createHash("sha256").update(ctx.location.directory).digest("hex");
    const dataHome = process.env.XDG_DATA_HOME || join(homedir(), ".local", "share");
    const data = join(dataHome, name, "opencode", directoryHash);

    await ctx.mcp.transform((editor) => {
      if (editor.get(name) !== undefined) return;

      editor.set(name, {
        type: "local",
        command: ["uv", "run", "--project", root, "--locked", "--no-dev", name],
        environment: {
          BROWSER_USER_DATA_DIR: process.env.BROWSER_USER_DATA_DIR || join(data, "user_data"),
          UV_PROJECT_ENVIRONMENT: join(data, ".venv"),
        },
        timeout: { startup: 360_000 },
        codemode: false,
      });
    });

    await ctx.skill.transform((editor) => {
      if (editor.get(name) !== undefined) return;

      editor.add({
        id: Skill.ID.make(name),
        name: Skill.Name.make("BrowserControl"),
        description: "Drive a live browser through BrowserControl using numbered screenshots.",
        path: Skill.Info.fields.path.make(skillPath),
        content,
      });
    });
  },
});
