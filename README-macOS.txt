Bili CC Extractor - macOS 使用说明

推荐方式：
1. 解压后，右键点击 Bili CC Extractor.app
2. 选择“打开”
3. 如果 macOS 提示无法验证开发者，请到“系统设置 → 隐私与安全性”中允许打开
4. 程序会自动准备运行环境，并打开浏览器

说明：
- 关闭浏览器页面不会停止后台服务。
- 需要退出程序时，请在网页右上角头像菜单中选择“关闭程序”。
- 如果再次打开 App 且后台已运行，会提示“打开浏览器”或“停止程序”。
- 本版本把 backend 内置在 App 中，并复制到 ~/Library/Application Support/Bili CC Extractor 运行，减少 macOS 对桌面/下载目录的隐私权限拦截。
- 日志保存在 ~/Library/Application Support/Bili CC Extractor/logs/macos-launch.log。

如果启动失败：
- 先查看上面的日志文件。
- 如果提示权限问题，可以打开“系统设置 → 隐私与安全性”，允许 Bili CC Extractor 访问文件。
- 如果提示缺少 Python，请安装 Python 3.10 或更高版本。
