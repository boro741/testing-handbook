// Mermaid's flowchart tooltips call selection.transition(). That method is added by d3-transition
// as a side effect, but d3 and d3-selection are marked "sideEffects: false", so the bundler drops it.
// Importing it here registers it. Without this, hovering a diagram node throws
// "tooltipElem.transition is not a function".
import 'd3-transition';
