# Roma Invicta: Byzantine Restoration

版本 0.2.0。以希腊开始新游戏，进入帝国政治、文化、宗教、领土光复、经济、企业及科研路线。保留已确认的国策名称，并加入最新数值调整与事件选择。

包含 77 个帝国国策、23 个自定义决议、18 个事件、14 位指挥官，以及移植的原版偿债决议。完整结构、逐节点效果和各分支累计奖励见 [当前完整国策与效果](docs/当前完整国策与效果.md)。陆军包含两条不互斥分支：罗马军团与现代铁甲圣骑兵，从帝国派登场接入，每线112天，加合流终点共259天；新增三名可任命理论家、陆军部长升级及军工奖励。

## 安装

便携压缩包：将其中 roma_restoration 文件夹及 roma_restoration.mod 解压到 Documents/Paradox Interactive/Hearts of Iron IV/mod/，在启动器中启用模组，以希腊开始新游戏。

直接使用当前工作目录：将本目录 roma_restoration.mod 复制到上述 mod 目录即可；它指向当前工作目录的绝对路径。不要同时启用两个副本。旧原型存档不受支持。

## 依赖与验证范围

需要 Battle for the Bosporus。军工机构内容需要 Arms Against Tyranny，实验设施内容需要 Gotterdammerung。人物头像与图标使用原版占位资源。

模组声明目标版本为 1.18.*，当前用于提取原版数据与静态检查的本地游戏是 1.19.2。尚未进行游戏内测试，也未验证 1.18 兼容性；启动器版本提示不代表完成兼容验证。改动包含原版希腊树、经济法和征兵法文件副本，与修改相同文件的其他模组可能冲突。

静态检查覆盖括号、引用、前置、互斥、州编号、本地化、关键数值，以及陆军分支独立性和军工奖励重复兑现回归。军工机构失去所在地后，已分配生产线与现有设计的引擎行为仍需游戏内确认。

## 生成与检查

使用 Python 执行 tools/build_mod.py --game 后跟本地 HOI4 目录，再执行 tools/build_reference.py 和 tools/validate_mod.py --game 后跟同一目录。生成器位于 tools/；验证报告位于 docs/validation_report.json。历史原型归档在 docs/prototype/。
