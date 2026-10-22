import { execFile } from "node:child_process";
import { Plugin } from "@opencode/plugin";

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang file and return stdout, stderr, and exit code.",
        input: {
          type: "object",
          properties: { filePath: { type: "string" } },
          required: ["filePath"],
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            stdout: { type: "string" },
            stderr: { type: "string" },
            exitCode: { type: "integer" },
          },
          required: ["stdout", "stderr", "exitCode"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { filePath } = input as { filePath: string };
          return {
            output: await runSlop(filePath, ctx.location.directory),
          };
        },
      });
    });
  },
});

export function runSlop(filePath: string, projectDirectory: string) {
  return new Promise<{ stdout: string; stderr: string; exitCode: number }>(
    (resolve, reject) => {
      execFile(
        "uv",
        ["run", "--no-active", "sloperator.py", filePath],
        { cwd: projectDirectory, encoding: "utf8", timeout: 10000 },
        (error, stdout, stderr) => {
          if (error && (error.killed || typeof error.code !== "number")) {
            reject(error);
            return;
          }
          resolve({
            stdout,
            stderr,
            exitCode: typeof error?.code === "number" ? error.code : 0,
          });
        },
      );
    },
  );
}
