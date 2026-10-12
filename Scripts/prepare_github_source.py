"""Export current code through a source/resource allowlist, preserving local Git."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('destination');a=p.parse_args();out=Path(a.destination).resolve()
if out.exists():raise SystemExit('Destination exists; use a fresh source snapshot.')
out.mkdir(parents=True)
allowed={'Sources':{'.swift'},'Backend':{'.py'},'Scripts':{'.py','.sh','.swift'},'Tests':{'.py','.swift','.json','.txt'},'Assets':{'.png','.jpg','.icns'},'Desktop':{'.cjs','.js','.css','.html','.json','.png','.ico'},'Vendor':{'.json','.xz','.bz2','.gz'},'.github':{'.yml','.yaml'}}
skip={'upstream','node_modules','__pycache__','resources','.electron-download'}
manifest={}
for folder,suffixes in allowed.items():
    for file in (root/folder).rglob('*'):
        relative=file.relative_to(root)
        if not file.is_file() or file.suffix not in suffixes or any(x in skip for x in relative.parts):continue
        dest=out/relative;dest.parent.mkdir(parents=True,exist_ok=True);data=file.read_bytes()
        if file.suffix in {'.swift','.py','.sh','.cjs','.js','.css','.html','.json','.txt','.yml','.yaml'}:
            text=data.decode('utf8');text=re.sub(r'/Users/[^/\s]+/Downloads/关系回响/QQ排程助手/', 'related-project/',text);data=text.encode('utf8')
        dest.write_bytes(data);shutil.copymode(file,dest);manifest[str(relative)]=hashlib.sha256(data).hexdigest()
for name in ['LICENSE','requirements-build.txt','.gitmodules']:shutil.copy2(root/name,out/name)
# Git records the original pin; do not publish a copy of local submodule metadata.
shutil.copytree(root/'Backend/upstream',out/'Backend/upstream',ignore=shutil.ignore_patterns('.git','__pycache__','.venv','.pytest_cache','*.pyc'))
(out/'.gitignore').write_text('.venv/\nnode_modules/\nbuild/\ndist/\nrelease-assets/\nDesktop/resources/\nDesktop/.electron-download/\n*.log\n*.app\n.DS_Store\n__pycache__/\n*.pyc\n')
(out/'AGENTS.md').write_text('# Shiying source rules\n\n- Keep the parsing submodule at the pinned commit in .gitmodules.\n- macOS uses Sources/; Windows uses Desktop/; both share Backend/.\n- Never commit logins, user libraries, media, private paths, or generated packages.\n- Validate source checks and the actual target-platform package before a release.\n- Do not edit a running installed app or its user data during builds.\n')
docs=out/'docs';docs.mkdir(exist_ok=True)
(out/'README.md').write_text('''# 拾影 Shiying

本地视频、图文与公众号素材工作台。Mac 使用原生 SwiftUI；Windows 使用适配的桌面界面和同一套 Python 下载内核。

## 下载

[最新版发行页](https://github.com/SJT-bright/shiying/releases/latest)

- Mac：Apple Silicon，macOS 26 或以上，下载 `Shiying-1.8.0-Mac-arm64.dmg`。
- Windows：Windows 10/11 x64，下载 `Shiying-1.8.0-Windows-x64-Setup.exe`；另有免安装 ZIP。
- 源码与媒体组件对应源码在同一发行页。安装包未做商业证书签名或 Apple 公证。

## 使用

在「新建下载」粘贴分享链接，选择画质、保存目录，点击「开始下载」。支持抖音、B站、小红书和视频号；各平台在内置网页中登录，状态保留在这台电脑的拾影中。视频号分享使用独立元宝登录解析，视频号助手登录不能代替元宝。网站登录或验证由用户完成。

图文先临时预览，可复制图片或确认保存，取消和离页清理未确认图片。批量队列按收藏夹整理，可暂停、重试并配套保存 M4A。已保存视频支持卡片内播放；资料有来源筛选、学习备注、真实目录移动和手动统计更新，缺失统计不按0处理。公众号文章独立保存 Markdown、离线 HTML 和原图；网页验证时可在内置页检查后读取当前正文。

公开接口的可访问范围取决于平台与当前登录；单条分享不代表作者全集。Mac 与 Windows 的登录和资料独立存储；发行包没有作者本机的登录、媒体和下载记录。

## 源码构建与许可

请看 [构建说明](docs/BUILD.md)、[第三方组件](docs/THIRD_PARTY.md) 与 [平台验证范围](docs/VALIDATION.md)。

本项目原创源码使用 MIT，解析子模块固定为 Apache-2.0 上游提交。FFmpeg 作为独立进程使用 GPL-3.0-or-later 构建，冻结的对应源码、配置与编译脚本均提供；Electron及其组件保留自己的许可。
''',encoding='utf8')
(docs/'BUILD.md').write_text('''# 构建

先用 `git clone --recurse-submodules` 获取源码，保持 Backend/upstream 的固定提交。Python 使用3.12，Node使用22；第三方 Python 版本由 requirements-build.txt 固定，桌面依赖由 Desktop/package-lock.json 固定。

## Mac arm64

创建 `.venv` 并安装 requirements-build.txt。使用 Homebrew 安装 pkgconf、nasm、meson、ninja。执行 `sh Scripts/build_media_tools.sh mac build/media-mac`，再执行 `Scripts/build_release_mac.sh build/media-mac/Tools`。打包会执行原有全部原生与后端回归门槛，输出DMG和ZIP到release-assets。

## Windows x64

媒体组件从 Vendor/MediaSources 的冻结源码在Linux用MinGW交叉构建：安装 mingw-w64、nasm、pkg-config、meson、ninja后，执行 `sh Scripts/build_media_tools.sh windows build/media-windows`。

在原生Windows环境安装 requirements-build.txt，执行 `python Scripts/build_windows.py --tools build/media-windows/Tools`。进入Desktop，执行 `npm ci`、`npm test`、`npm run build:win`。GitHub Actions完成原生Windows组件、后端、打包启动、便携包和安装后的验证，不能用Mac交叉打包结果代替这些检查。

数据保存在当前用户应用数据目录；开发与self-test模式使用独立资料根，不读正式Mac资料。
''',encoding='utf8')
(docs/'THIRD_PARTY.md').write_text('''# 第三方组件

- Evil0ctal/Douyin_TikTok_Download_API：Apache-2.0，固定提交4f0bed8483c35a980315d9c7b3a1d4a1119ad2b2，保留原许可证。
- Python依赖与yt-dlp：固定版本及许可随包提供。
- Electron44.7.0：MIT及Chromium第三方许可；发行包含LICENSE与LICENSES.chromium.html。原始实现与构建说明见https://github.com/electron/electron/tree/v44.7.0。
- FFmpeg9.0.1：GPL-3.0-or-later，本版使用libx264、dav1d和OpenSSL，独立进程运行。所有媒体构建源包在Vendor/MediaSources，原始URL和SHA256记录在sources.json；脚本保留确切配置。发行页也附对应源包，不使用enable-nonfree构建。
- x264：GPL-2.0-or-later；dav1d：BSD-2-Clause；OpenSSL：Apache-2.0。完整许可在对应源包内。

来源：[FFmpeg许可](https://ffmpeg.org/legal.html)、[Electron安全与发行文档](https://www.electronjs.org/docs/latest/tutorial/security)。第三方保留自己的许可，不被项目MIT声明覆盖。
''',encoding='utf8')
(docs/'VALIDATION.md').write_text('''# 平台验证范围

Mac与Windows使用相同下载/图文/文章/统计内核，界面按系统适配。Mac原生功能以现有源码与回归门槛为基础；Windows发行流程在Windows运行真实.exe、真实FFmpeg及安装后的应用。

自动检查覆盖中文与空格路径、视频编码与音频、进度事件、播放器字节范围读取、隔离登录存储、取消任务、资料持久化和目录移动。浏览器安全边界和字段来源由固定允许列表控制。合成登录检查不等同平台账号当前有效；用户在各自电脑首次使用时需要在内置网页登录。

发布前以Actions与发布回执的实际结果为准，不把源码上传或打包成功称为所有平台在线下载验收。
''',encoding='utf8')
(docs/'index.md').write_text('# 资料索引\n\n- [构建](BUILD.md)：按平台复现打包。\n- [第三方组件](THIRD_PARTY.md)：许可、来源与冻结源码。\n- [验证范围](VALIDATION.md)：区分代码检查、实际包和在线账号。\n')
(docs/'log.md').write_text('# 发布日志\n\n- 2026-10-12：从当前1.7.5业务基线适配Windows桌面，共享内核新增Windows文件名、组件路径及取消信号处理。发布目标1.8.0；最终发行资产以GitHub Release为准。\n')
(out/'source-snapshot.json').write_text(json.dumps({'baseVersion':'1.7.5','releaseVersion':'1.8.0','upstream':'4f0bed8483c35a980315d9c7b3a1d4a1119ad2b2','files':manifest},indent=2)+'\n')
subprocess.run(['python3',str(root/'Scripts/audit_release.py'),str(out),'--source'],check=True)
print('Sanitized source snapshot prepared: '+str(out))
