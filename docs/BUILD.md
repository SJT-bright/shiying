# 构建

先用 `git clone --recurse-submodules` 获取源码，保持 Backend/upstream 的固定提交。Python 使用3.12，Node使用22；第三方 Python 版本由 requirements-build.txt 固定，桌面依赖由 Desktop/package-lock.json 固定。

## Mac arm64

创建 `.venv` 并安装 requirements-build.txt。使用 Homebrew 安装 pkgconf、nasm、meson、ninja。执行 `sh Scripts/build_media_tools.sh mac build/media-mac`，再执行 `Scripts/build_release_mac.sh build/media-mac/Tools`。打包会执行原有全部原生与后端回归门槛，输出DMG和ZIP到release-assets。

## Windows x64

媒体组件从 Vendor/MediaSources 的冻结源码在Linux用MinGW交叉构建：安装 mingw-w64、nasm、pkg-config、meson、ninja后，执行 `sh Scripts/build_media_tools.sh windows build/media-windows`。

在原生Windows环境安装 requirements-build.txt，执行 `python Scripts/build_windows.py --tools build/media-windows/Tools`。进入Desktop，执行 `npm ci`、`npm test`、`npm run build:win`。GitHub Actions完成原生Windows组件、后端、打包启动、便携包和安装后的验证，不能用Mac交叉打包结果代替这些检查。

数据保存在当前用户应用数据目录；开发与self-test模式使用独立资料根，不读正式Mac资料。
