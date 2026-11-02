// How this plugin's page draws its task output: the submit verdict with
// the expression judged, the answer given, and each constraint checked.
import { h, icon, statusPill } from "./kit/components.js";

/** Render a SubmitOutput verdict. */
export function renderSubmit(output) {
  const passed = output.verdict === "pass";
  const root = h("div", { class: "validity-verdict" });

  // Header — pass / fail pill
  const header = h("div", { class: "validity-header" });
  header.append(statusPill(passed ? "pass" : "fail", passed ? "ok" : "bad"));
  header.append(h("span", { class: "validity-score", text: `Score: ${output.score.toFixed(1)}` }));
  root.append(header);

  // Constraints list
  const list = h("ol", { class: "checks" });
  for (const c of output.constraints) {
    const ok = c.ok;
    const item = h("li", { class: ok ? "check-ok" : "check-bad" });
    const head = h("div", { class: "check-head" });
    head.append(icon(ok ? "check-circle" : "x-circle"));
    head.append(h("span", { text: c.detail }));
    head.append(h("span", { class: "check-id", text: c.id }));
    item.append(head);
    list.append(item);
  }
  root.append(list);
  return root;
}

// Default export keyed by output class name, as NanoAgent expects.
export default {
  SubmitOutput: renderSubmit,
};
