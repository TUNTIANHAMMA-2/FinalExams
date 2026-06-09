/**
 * Global frontend configuration and constants.
 */

export const ASCII_CHARS = ' .,:;irsXA253hMHGS#9B&@';
export const ASCII_WIDTH = 280;
export const ASCII_FRAME_INTERVAL_MS = 80;
export const RECOGNITION_INTERVAL_MS = 1600;

/**
 * ASCII 渲染几何参数 —— 让字符画比例还原并自适应容器。
 *
 * 采样行数 = 列数 × 视频高宽比 × (ASCII_CHAR_ASPECT / ASCII_LINE_HEIGHT)，
 * 使「列数×字符宽 : 行数×行高」= 视频真实宽高比（消除横向拉伸）。
 * 字号则由 ResizeObserver 按容器实际宽高动态计算（不再用 vw）。
 */
export const ASCII_LINE_HEIGHT = 0.65; // <pre> 行高（em），与 index.css 中保持一致
export const ASCII_CHAR_ASPECT = 0.6; // 等宽字符单元宽/字号的回退值，运行时会实测校正
