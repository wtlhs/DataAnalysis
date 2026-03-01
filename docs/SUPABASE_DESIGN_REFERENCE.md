# Supabase 风格设计参考

## 设计理念

Supabase 的设计语言体现了"专业、现代、可信赖"的价值观，通过以下核心特征体现：

- **精致的技术美学**：深色背景 + 鲜亮点缀
- **流畅的交互体验**：细腻的动画和过渡
- **清晰的视觉层次**：统一的信息架构
- **现代科技感**：适度的玻璃拟态和发光效果

---

## 色彩系统

### 主色调

```css
/* 深色背景 */
--bg-background: #09090b;           /* 主背景 - 深蓝黑色 */
--bg-surface: #1e293b;            /* 卡片表面 - 更深的蓝灰 */
--bg-surface-elevated: #18181b;  /* 悬停表面 - 稍微更亮的蓝灰 */
--bg-elevated: #27272a;             /* 悬停元素 - 略亮的蓝灰 */

/* 文字颜色 */
--text-primary: #e2e8f0;           /* 主文字 - 亮白色 */
--text-secondary: #94a3b8;         /* 次要文字 - 浅灰白色 */
--text-muted: #64748b;             /* 弱化文字 - 灰白色 */
--text-inverse: #09090b;            /* 深色文字 - 在深色背景上 */

/* 边框和分割线 */
--border: #2c3e50;               /* 细边框 - 半透明深灰 */
--border-subtle: #334155;           /* 细微边框 */
--border-strong: #525e5f7;           /* 强边框 - 更不透明的深灰 */

/* 功能色（鲜艳但专业） */
--accent-blue: #3b82f6;            /* 蓝色 - 主要强调 */
--accent-emerald: #10b981;          /* 翠绿色 - 成功状态 */
--accent-violet: #8b5cf6;           /* 紫色 - 特殊功能 */
--accent-pink: #ec4899;              /* 粉色 - 删除操作 */

/* 玻璃拟态渐变 */
--gradient-blue: linear-gradient(135deg, #1e293b 0%, #18181b 100%);
--gradient-emerald: linear-gradient(135deg, #059669 0%, #10b981 100%);
--gradient-violet: linear-gradient(135deg, #2d1b2e 0%, #3b82f6 100%);
```

---

## 卡片设计系统

### 基础卡片结构

```css
.supabase-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 0.625rem;
    padding: 1.25rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.supabase-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg,
        rgba(255, 255, 255, 0.03) 0%,
        rgba(255, 255, 255, 0) 100%);
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.supabase-card:hover {
    transform: translateY(-2px);
    box-shadow:
        0 0 0 1px rgba(0, 0, 0, 0.1),
        0 4px 8px rgba(0, 0, 0, 0.05),
        0 0 20px rgba(59, 130, 246, 0.15);
    border-color: var(--border);
}

/* 玻璃拟态发光效果 */
.supabase-card-glow {
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: radial-gradient(
        100px at 0 0,
        rgba(59, 130, 246, 0.3) 0%,
        transparent 50%
    );
    filter: blur(30px);
    opacity: 0.5;
    pointer-events: none;
    transition: all 0.3s ease;
}

.supabase-card-glow::after {
    content: '';
    position: absolute;
    inset: 2px;
    border-radius: calc(0.625rem - 2px);
    background: var(--bg-surface);
}
```

### 内容卡片

```css
.supabase-card-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.supabase-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.75rem;
}

.supabase-card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
}

.supabase-card-description {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.5;
}
```

---

## 按钮系统

### 主按钮

```css
.supabase-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    border: 1px solid transparent;
    background: var(--gradient-blue);
    color: var(--text-primary);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.supabase-button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg,
        rgba(255, 255, 255, 0.1) 0%,
        transparent 50%
    );
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.supabase-button:hover {
    transform: translateY(-1px);
    box-shadow:
        0 0 10px rgba(59, 130, 246, 0.4),
        0 0 0 1px rgba(255, 255, 255, 0.2);
    border-color: var(--border);
}

.supabase-button:active {
    transform: translateY(0);
}

/* 发光效果 */
.supabase-button-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(
        100px at 50% 0,
        rgba(59, 130, 246, 0.6) 0%,
        transparent 50%
    );
    filter: blur(20px);
    opacity: 0;
    pointer-events: none;
    transition: all 0.3s ease;
}

.supabase-button:hover .supabase-button-glow {
    opacity: 0.6;
}
```

### 次要按钮

```css
.supabase-button-secondary {
    background: var(--bg-surface);
    border-color: var(--border-subtle);
    color: var(--text-primary);
}

.supabase-button-secondary:hover {
    background: var(--bg-surface-elevated);
    border-color: var(--border);
}
```

### 幽灵按钮

```css
.supabase-button-ghost {
    background: transparent;
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
}

.supabase-button-ghost:hover {
    background: rgba(59, 130, 246, 0.1);
    border-color: var(--border);
    color: var(--text-primary);
}
```

---

## 输入框系统

### 主要输入框

```css
.supabase-input {
    width: 100%;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 0.375rem;
    padding: 0.625rem 0.875rem;
    font-size: 0.875rem;
    color: var(--text-primary);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.supabase-input:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow:
        0 0 0 1px rgba(59, 130, 246, 0.5),
        0 0 0 4px rgba(59, 130, 246, 0.15);
    background: var(--bg-background);
}

.supabase-input::placeholder {
    color: var(--text-muted);
}

/* 输入标签 */
.supabase-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 0.375rem;
}

.supabase-label-required {
    color: var(--accent-pink);
}
```

---

## 表格系统

### 数据表格

```css
.supabase-table-container {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 0.625rem;
    overflow: auto;
}

.supabase-table {
    width: 100%;
    border-collapse: collapse;
}

.supabase-table thead {
    background: linear-gradient(90deg, var(--bg-surface-elevated) 0%, var(--bg-surface) 100%);
    color: var(--text-primary);
    font-weight: 600;
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    border-bottom: 1px solid var(--border-subtle);
}

.supabase-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-secondary);
}

.supabase-table tbody tr:hover {
    background: rgba(59, 130, 246, 0.03);
}

.supabase-table tbody tr:last-child td {
    border-bottom: none;
}
```

---

## 动画系统

### 页面加载

```css
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.supabase-page-enter {
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 内容进入动画 - 交错的 */
@keyframes staggerIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.supabase-stagger-item:nth-child(1) { animation-delay: 0ms; }
.supabase-stagger-item:nth-child(2) { animation-delay: 50ms; }
.supabase-stagger-item:nth-child(3) { animation-delay: 100ms; }
.supabase-stagger-item:nth-child(4) { animation-delay: 150ms; }
.supabase-stagger-item:nth-child(5) { animation-delay: 200ms; }
.supabase-stagger-item:nth-child(6) { animation-delay: 250ms; }
```

### 悬停效果

```css
.supabase-hover-lift {
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.supabase-hover-lift:hover {
    transform: translateY(-3px);
    box-shadow:
        0 4px 8px rgba(0, 0, 0, 0.1),
        0 0 10px rgba(59, 130, 246, 0.15);
}
```

### 加载动画

```css
@keyframes shimmer {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

.supabase-skeleton {
    background: linear-gradient(
        90deg,
        var(--bg-surface) 25%,
        var(--bg-surface-elevated) 50%,
        var(--bg-surface) 50%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.25rem;
}

.supabase-skeleton-text {
    background: var(--bg-surface-elevated);
    height: 0.75rem;
    border-radius: 0.125rem;
    margin: 0.375rem 0.5rem;
    width: 40%;
}
```

---

## 间距系统

### 统一间距标准

```css
/* 间距单位 */
--space-xs: 0.25rem;
--space-sm: 0.375rem;
--space-md: 0.625rem;
--space-lg: 1rem;
--space-xl: 1.5rem;
--space-2xl: 2rem;

/* 组件内边距 */
.supabase-card { padding: var(--space-lg); }
.supabase-button { padding: var(--space-sm) var(--space-md); }
.supabase-input { padding: var(--space-sm) var(--space-md); }

/* 组件间距 */
.gap-xs { gap: var(--space-xs); }
.gap-sm { gap: var(--space-sm); }
.gap-md { gap: var(--space-md); }
.gap-lg { gap: var(--space-lg); }
.gap-xl { gap: var(--space-xl); }
```

---

## 字体系统

### 字体栈

```css
/* 主要使用 Inter 字体系列 */
--font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 等宽字体 */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
```

### 字体大小

```css
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.5rem;
--text-2xl: 2rem;
--text-3xl: 2.5rem;

--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

---

## 阴影系统

### 阴影层次

```css
--shadow-sm:
    0 1px 2px rgba(0, 0, 0, 0.05),
    0 0 0 1px rgba(0, 0, 0, 0.1);

--shadow:
    0 4px 8px rgba(0, 0, 0, 0.1),
    0 0 10px rgba(0, 0, 0, 0.15);

--shadow-lg:
    0 10px 15px -2px rgba(0, 0, 0, 0.05),
    0 0 20px -3px rgba(0, 0, 0, 0.1);

--shadow-glow:
    0 0 20px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(59, 130, 246, 0.6);
```

---

## 圆角系统

```css
--radius-sm: 0.25rem;
--radius: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
--radius-full: 9999px;
```

---

## 状态指示器

### 加载状态

```html
<div class="supabase-loading">
    <div class="loading-spinner"></div>
    <span class="loading-text">加载中...</span>
</div>

<style>
.supabase-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 2rem;
}

.loading-spinner {
    width: 1.5rem;
    height: 1.5rem;
    border: 2px solid var(--border-subtle);
    border-top-color: var(--accent-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-text {
    color: var(--text-secondary);
    font-size: 0.875rem;
}
</style>
```

---

## 徽章和标签系统

### 标签

```css
.supabase-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
}

/* 标签变体 */
.supabase-tag-default {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
}

.supabase-tag-emerald {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
    color: var(--text-primary);
}

.supabase-tag-blue {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.2);
    color: var(--text-primary);
}

.supabase-tag-violet {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.2);
    color: var(--text-primary);
}
```

---

## 模态对话框

```css
.supabase-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: modalFadeIn 0.2s ease;
}

@keyframes modalFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.supabase-modal {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    box-shadow: var(--shadow-glow);
    max-width: 500px;
    width: 90%;
    animation: modalSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalSlideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.supabase-modal-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.supabase-modal-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
}

.supabase-modal-close {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.375rem;
    transition: all 0.15s ease;
}

.supabase-modal-close:hover {
    background: var(--bg-surface);
    color: var(--text-primary);
}

.supabase-modal-body {
    padding: 1rem;
}
```

---

## 工具提示

```html
<div class="supabase-tooltip">
    <div class="tooltip-content">提示内容</div>
    <div class="tooltip-arrow"></div>
</div>

<style>
.supabase-tooltip {
    position: relative;
}

.tooltip-content {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    color: var(--text-primary);
    max-width: 200px;
    opacity: 0;
    animation: tooltipFade 0.2s ease forwards;
    pointer-events: none;
}

@keyframes tooltipFade {
    from {
        opacity: 0;
        transform: translateY(5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.tooltip-arrow {
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid var(--border);
}

.tooltip-arrow::before {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid var(--bg-surface);
}
</style>
```

---

## 分页导航

```html
<div class="supabase-pagination">
    <button class="pagination-item" disabled>上一页</button>
    <span class="pagination-info">第 1 / 5 页</span>
    <button class="pagination-item">下一页</button>
</div>

<style>
.supabase-pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.pagination-item {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 0.375rem;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
}

.pagination-item:hover:not(:disabled) {
    background: var(--bg-surface-elevated);
    color: var(--text-primary);
    border-color: var(--border);
}

.pagination-item:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-info {
    color: var(--text-muted);
    font-size: 0.875rem;
}
</style>
```

---

## 进度条

```html
<div class="supabase-progress-container">
    <div class="progress-bar">
        <div class="progress-fill" style="width: 65%;"></div>
    <span class="progress-text">65%</span>
    </div>
    <span class="progress-status">处理中...</span>
</div>

<style>
.supabase-progress-container {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
}

.progress-bar {
    height: 0.5rem;
    background: var(--bg-surface);
    border-radius: 9999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-emerald));
    border-radius: 9999px;
    transition: width 0.3s ease;
    animation: progressPulse 2s ease-in-out infinite;
}

@keyframes progressPulse {
    0%, 100% {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    opacity: 0.8;
    }
    50%, 0% {
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
        opacity: 1;
    }
}

.progress-text {
    position: absolute;
    right: 0.75rem;
    color: var(--text-primary);
    font-size: 0.75rem;
    font-weight: 600;
}

.progress-status {
    font-size: 0.875rem;
    color: var(--text-muted);
}
</style>
```

---

## 通知徽章

```html
<div class="supabase-badge">
    <span class="badge-icon">✓</span>
    <span class="badge-count">3</span>
</div>

<style>
.supabase-badge {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.badge-count {
    background: var(--accent-pink);
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.125rem 0.375rem;
    border-radius: 9999px;
}

.badge-icon {
    font-size: 0.875rem;
    margin-right: 0.25rem;
}
</style>
```

---

## 应用到数据分析应用的映射

### 主页面背景

```css
body {
    background: var(--bg-background);
    color: var(--text-primary);
    font-family: var(--font-sans);
}
```

### 功能卡片映射

```css
/* 数据上传卡片 */
.upload-card → .supabase-card + .upload-icon

/* 数据预览卡片 */
.preview-card → .supabase-card + .preview-icon

/* 统计分析卡片 */
.analysis-card → .supabase-card + .analysis-icon

/* 预测卡片 */
.prediction-card → .supabase-card + .prediction-icon

/* 风险预警卡片 */
.risk-card → .supabase-card + .risk-icon

/* AI 分析卡片 */
.ai-card → .supabase-card + .ai-icon

/* 报告卡片 */
.report-card → .supabase-card + .report-icon
```

### 页面布局建议

1. **卡片网格系统**
   - 移动端：2列网格
   - 平板端：3-4列网格
   - 桌面端：自动填充

2. **响应式边距**
   - 移动端：1.5rem 外边距
   - 桌面端：2rem 外边距

3. **导航栏布局**
   - 顶部：深色渐变背景 + Logo
   - 搜索框：深色表面 + 发光聚焦
   - 模式切换：标签页 + 活动指示器

---

## 设计最佳实践

1. **保持一致性**
   - 所有卡片使用相同的间距和圆角
   - 所有按钮使用相同的动画时长
   - 所有输入框使用相同的聚焦状态

2. **适度使用效果**
   - 玻璃拟态：仅用于关键卡片和对话框
   - 发光效果：仅用于主要操作按钮
   - 动画：避免同时过多的动画

3. **注重性能**
   - 使用 CSS transform 而不是 layout
   - 避免过度的 box-shadow
   - 使用 will-change 优化重绘

4. **可访问性考虑**
   - 保持足够的颜色对比度
   - 所有交互元素有清晰的焦点状态
   - 键盘导航支持

---

## 快速实现指南

### 阶段1：核心样式

1. 将上述 CSS 变量添加到样式表
2. 实现基础卡片组件类
3. 实现按钮系统（主/次要/幽灵）
4. 实现输入框样式

### 阶段2：功能组件

1. 实现标签系统
2. 实现进度条
3. 实现加载骨架屏
4. 实现通知徽章

### 阶段3：高级功能

1. 实现模态对话框
2. 实现工具提示
3. 实现表格样式
4. 实现分页导航

---

## 文件清单

需要创建的文件：
- `supabase-design.css` - 完整的 Supabase 风格样式文件
- `ui/supabase_components.py` - Supabase 风格 UI 组件库

---

**设计原则总结**：
1. ✨ **精致** - 每个细节都经过精心设计
2. 🎯 **现代** - 使用最新的设计趋势和技术
3. 🔬 **专业** - 适合企业级应用
4. 💪 **一致** - 统一的设计语言和模式
5. ⚡ **高效** - 性能优化的实现方案

参考 Supabase 官网：https://supabase.com/
