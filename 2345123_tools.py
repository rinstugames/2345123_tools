import os
import hashlib
import psutil
import shutil
import winreg
import sys
import ctypes
from glob import glob
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

class KillerGUI:
    def __init__(self, root):
        ctk.set_appearance_mode("system")  
        ctk.set_default_color_theme("blue")
        self.root = root
        self.root.title("隆度专杀工具")
        self.root.geometry("650x540")
        self.root.resizable(False, False)
        try:
            icon_path = os.path.join(os.path.dirname(sys.argv[0]), 'icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        self.root.wm_attributes('-transparentcolor', '#f0f0f0')
        self.root.configure(bg='#f0f0f0')
        try:
            self.root.wm_attributes('-alpha', 0.96)  
        except Exception:
            pass

        self.show_notice()

        warning = ctk.CTkLabel(root, text="⚠使用前请务必：备份重要数据、以管理员权限运行此程序、确保没有重要程序正在运行", text_color="red", font=("微软雅黑", 13, "bold"))
        warning.pack(pady=12)

        btn_frame = ctk.CTkFrame(root, fg_color=("#f8fafd", "#222c37"), corner_radius=18)
        btn_frame.pack(pady=8)
        self.start_btn = ctk.CTkButton(btn_frame, text="开始查杀", width=120, command=self.start_scan, font=("微软雅黑", 14, "bold"), corner_radius=16)
        self.start_btn.grid(row=0, column=0, padx=16, pady=8)

class KillerGUI:
    def __init__(self, root):
        ctk.set_appearance_mode("system")  
        ctk.set_default_color_theme("blue")
        self.root = root
        self.root.title("隆度专杀工具")
        self.root.geometry("650x540")
        self.root.resizable(False, False)
        self.root.wm_attributes('-transparentcolor', '#f0f0f0')
        self.root.configure(bg='#f0f0f0')
        try:
            self.root.wm_attributes('-alpha', 0.96)  
        except Exception:
            pass

        self.show_notice()

        warning = ctk.CTkLabel(root, text="⚠使用前请务必：备份重要数据、以管理员权限运行此程序、确保没有重要程序正在运行", text_color="red", font=("微软雅黑", 13, "bold"))
        warning.pack(pady=12)

        btn_frame = ctk.CTkFrame(root, fg_color=("#f8fafd", "#222c37"), corner_radius=18)
        btn_frame.pack(pady=8)
        self.start_btn = ctk.CTkButton(btn_frame, text="开始查杀", width=120, command=self.start_scan, font=("微软雅黑", 14, "bold"), corner_radius=16)
        self.start_btn.grid(row=0, column=0, padx=16, pady=8)
        self.stop_btn = ctk.CTkButton(btn_frame, text="停止", width=120, command=self.stop_scan, state="disabled", font=("微软雅黑", 14), corner_radius=16)
        self.stop_btn.grid(row=0, column=1, padx=16, pady=8)
        self.close_btn = ctk.CTkButton(btn_frame, text="关闭程序", width=120, command=self.root.quit, font=("微软雅黑", 14), corner_radius=16)
        self.close_btn.grid(row=0, column=2, padx=16, pady=8)

        self.progress_var = ctk.DoubleVar()
        self.progress = ctk.CTkProgressBar(root, variable=self.progress_var, width=500, height=18, corner_radius=10)
        self.progress.pack(pady=14)
        self.progress.set(0)

        log_label = ctk.CTkLabel(root, text="操作日志：", font=("微软雅黑", 12))
        log_label.pack(anchor='w', padx=24)
        self.log_box = ctk.CTkTextbox(root, width=600, height=270, font=("Consolas", 11), corner_radius=12)
        self.log_box.pack(padx=12, pady=8)
        self.log_box.configure(state="disabled")

        self.scanning = False
        self.scan_thread = None

    def show_notice(self):
        notice = (
            "温馨提示：为达到最佳查杀效果，本软件会扫描用户的内存（RAM）和硬盘（HardDisk），扫描过程只会在本地运行，本软件不会也完全不需要连接互联网。\n"
            "不会收集任何用户数据和信息，不会上传任何数据。本软件在GitHub平台上开放全部源代码，任何人都可以查看、审阅、修改、删减、转发、逆向、再编译本软件。\n"
            "亦可商业化使用、销售、或基于本软件开发其它软件，本软件是完全免费、开源的Copyleft自由软件，遵循GPLv3协议。\n"
            "病毒程序修改了IE、Edge、Chrome、Firefox、Opera、obs、7Z、各类视频播放器的默认配置和程序运行库，故本工具为了彻底杀灭病毒，可能会对上述程序造成一定影响，建议杀毒结束后重装上述软件。\n"
            "开始扫描前请先备份您的重要文件和数据，本软件有概率会对您的重要文件造成损害，请知悉。"
        )
        messagebox.showinfo("温馨提示", notice)

    def start_scan(self):
        if self.scanning:
            return
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "[INFO] 开始查杀...\n")
        self.log_box.configure(state="disabled")
        self.progress_var.set(0)
        self.progress.configure(state="normal")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.scanning = True
        self.scan_thread = threading.Thread(target=self.run_kill)
        self.scan_thread.start()

    def stop_scan(self):
        self.scanning = False
        self.log_box.configure(state="normal")
        self.log_box.insert("end", "[WARN] 用户请求停止查杀。\n")
        self.log_box.configure(state="disabled")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress.configure(state="disabled")

    def run_kill(self):
        steps = [
            ("正在杀掉相关进程...", lambda: kill_processes(set(VIRUS_NAMES))),
            ("正在清理启动项...", lambda: remove_startup_items(set(VIRUS_NAMES))),
            ("正在清理右键菜单...", remove_context_menu),
            ("正在删除2345王牌输入法...", remove_2345pinyin_ime),
            ("正在删除控制面板卸载项...", remove_uninstall_entries),
            ("正在删除组策略项...", remove_group_policy),
            ("正在删除相关注册表项...", remove_related_registry),
            ("正在全盘查杀病毒文件...", search_and_delete_virus),
            ("正在恢复浏览器主页和清理快捷方式...", restore_browser_shortcuts),
            ("正在删除常见桌面快捷方式...", self.remove_shortcuts),
            ("查杀完成！请重启电脑。", None)
        ]
        total = len(steps)
        for idx, (msg, func) in enumerate(steps):
            if not self.scanning:
                break
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[STEP] {msg}\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
            if func:
                try:
                    func()
                except Exception as e:
                    self.log_box.configure(state="normal")
                    self.log_box.insert("end", f"[ERROR] {msg} 失败: {e}\n")
                    self.log_box.configure(state="disabled")
            self.progress_var.set((idx+1)/total*100)
        self.scanning = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress.configure(state="disabled")

    def remove_shortcuts(self):
        known_shortcuts = [
            '2345OCR文字识别.lnk', '2345PDF转换器.lnk', '2345加速浏览器.lnk', '2345安全卫士.lnk', '2345桌面.lnk',
            '2345游戏大厅.lnk', '2345网址导航.lnk', '360PDF转换.lnk', '360办公助手.lnk', '360壁纸.lnk',
            '360游戏大厅.lnk', 'Hao123.lnk', '好压.lnk', '小鸟动态壁纸.lnk', '影视大全.lnk', '快压.lnk',
            '恒星播放器.lnk', '极速浏览器.lnk', '看图王.lnk', '软件管家.lnk', '驱动人生.lnk'
        ]
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        for shortcut in known_shortcuts:
            shortcut_path = os.path.join(desktop, shortcut)
            try:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
            except Exception:
                pass

def main_gui():
    root = ctk.CTk()
    app = KillerGUI(root)
    root.mainloop()

if not ctypes.windll.shell32.IsUserAnAdmin():
    print("请以管理员身份运行本程序！")
    sys.exit(1)


C_DRIVE = 'C:\\'
WINDOWS_DIR = os.path.join(C_DRIVE, 'Windows')
DESKTOP = os.path.join(os.environ['USERPROFILE'], 'Desktop')
BROWSER_NAMES = [
    'Internet Explorer', 'Microsoft Edge', 'Google Chrome', 'Firefox', 'Chromium', 'Opera'
]
BROWSER_EXE = [
    'iexplore.exe', 'msedge.exe', 'chrome.exe', 'firefox.exe', 'chromium.exe', 'opera.exe'
]
KEYWORDS = ['2345', 'hao123', '二三四五', '2345.com', 'hao123.com', '快压', '好压', 'Stellar', 'TSBrowser', 'kuaizip', 'haozip', 'abckantu', 'birdpaper', 'DriveTheLife', 'DGSetup_Home_KZ', '恒星播放器']

VIRUS_NAMES = [
    '2345AdRtProtect.exe',
    '2345Associate.exe',
    '2345AuthorityProtect.exe',
    '2345Cad.exe',
    '2345Capture.exe',
    '2345Desktop.exe',
    '2345DesktopLoader.exe',
    '2345DesktopService.exe',
    '2345Explorer.exe',
    '2345explorer_000435.exe',
    '2345ExtShell.exe',
    '2345ExtShell64.exe',
    '2345FileShre.exe',
    '2345gamebox_7cc75f8a.exe',
    '2345HipsSet.exe',
    '2345InstDll.exe',
    '2345LeakFixer.exe',
    '2345Login.exe',
    '2345LSPFix.exe',
    '2345ManuUpdate.exe',
    '2345Movie.exe',
    '2345MPCSafe.exe',
    '2345NetFlow.exe',
    '2345NetRepair.exe',
    '2345NightMode.exe',
    '2345OCRDumper.exe',
    '2345OCRExecutor.exe',
    '2345OCRLoader.exe',
    '2345OCRMain.exe',
    '2345OCRUpdate.exe',
    '2345OCR_000001_v1.2.0.243.exe',
    '2345PCSafeBootAssistant.exe',
    '2345PdfConverter_000002_v2.9.0.823.exe',
    '2345PdfDumper.exe',
    '2345PdfEditor.exe',
    '2345PdfFeedback.exe',
    '2345PdfHelper.exe',
    '2345PdfLoader.exe',
    '2345PdfMain.exe',
    '2345PdfProcess.exe',
    '2345PdfReader.exe',
    '2345PdfTool.exe',
    '2345PdfUpdate.exe',
    '2345PdfWorker.exe',
    '2345Pic.exe',
    '2345PicCapture.exe',
    '2345PicDumper.exe',
    '2345PicEdit.exe',
    '2345PicEditor.exe',
    '2345PicFeedback.exe',
    '2345PicHelper.exe',
    '2345PicHome.exe',
    '2345PicLoader.exe',
    '2345PicPrinter.exe',
    '2345PicTool.exe',
    '2345PicUpdate.exe',
    '2345PicViewer.exe',
    '2345PicWorker.exe',
    '2345pic_000002_v13.1.0.11876.exe',
    '2345PinyinCloud.exe',
    '2345PinyinConfig.exe',
    '2345PinyinInstall.exe',
    '2345PinyinInstall64.exe',
    '2345PinyinSkinUtil.exe',
    '2345PinyinSymbol.exe',
    '2345PinyinTool.exe',
    '2345PinyinUpdate.exe',
    '2345PinyinWizard.exe',
    '2345pinyin_000003_v7.9.1.8335.exe',
    '2345PreviewWorker.exe',
    '2345ProtectManager.exe',
    '2345RTProtect.exe',
    '2345RtProtectCenter.exe',
    '2345SafeCenterCrashReport.exe',
    '2345SafeCenterInstaller.exe',
    '2345SafeCenterSvc.exe',
    '2345SafeCenterUpdate.exe',
    '2345SafeLock.exe',
    '2345SafeSvc.exe',
    '2345SafeTray.exe',
    '2345SafeUpdate.exe',
    '2345ScUpgrade.exe',
    '2345Setting.exe',
    '2345SFGuard.exe',
    '2345SFGuard64.exe',
    '2345SFWebShell.exe',
    '2345ShellPro.exe',
    '2345ShortcutArrow.exe',
    '2345SoftInstallAgent.exe',
    '2345SoftMgr.exe',
    '2345SoftMgrShell.exe',
    '2345SoftMgrShell64.exe',
    '2345SysDoctor.exe',
    '2345TrashRcmd.exe',
    '2345Uninst.exe',
    '2345UsbGuard.exe',
    '2345VirusScan.exe',
    '2345_softmgr_movie_000003.exe',
    '360AlbumViewerUpdate.exe',
    '360bdoctor.exe',
    '360chromeup.exe',
    '360DeskAna.exe',
    '360DeskAna64.exe',
    '360DesktopBackup.exe',
    '360DesktopLite.exe',
    '360DesktopLite64.exe',
    '360DesktopLite_zm000001.exe',
    '360DesktopService.exe',
    '360DesktopService64.exe',
    '360Feedback.exe',
    '360Game.exe',
    '360game5_setup.exe',
    '360hb4.0.434.0__1003__.exe',
    '360huabao.exe',
    '360huabaosetup.exe',
    '360ScreenCapture.exe',
    '360se.exe',
    '360searchlite.exe',
    '360secore.exe',
    '360seupdate.exe',
    '360SudaExtInstaller.exe',
    '360theme.exe',
    '360wpapp.exe',
    '360wpsrv.exe',
    '360办公助手-AI文档处理.exe',
    'aapt.exe',
    'abckantu_v3.2.2.8.exe',
    'adb.exe',
    'AndrowsInstaller.exe',
    'AssistExplorer.exe',
    'AssistHaoZip.exe',
    'AssistPic.exe',
    'AssistPinyin.exe',
    'BeautifyProxy.exe',
    'BeautifyProxy64.exe',
    'BirdHelper.exe',
    'birdpaper_home.exe',
    'BirdPlayer.exe',
    'birdsrv.exe',
    'birdsrvhost.exe',
    'birdtray.exe',
    'birdupd.exe',
    'BirdWallpaper.exe',
    'birdwp.exe',
    'BoxDoctor.exe',
    'BrowserService.exe',
    'BrowserServiceManager.exe',
    'CefView.exe',
    'ComputerZ12_helper.exe',
    'CrashReport.exe',
    'CrashSender1403.exe',
    'DesklitePlatform.exe',
    'DGSetup_Home_KZ.exe',
    'Doctor_2345Explorer.exe',
    'Down.exe',
    'DriveTheLife.exe',
    'DriveTheLife_2571_10_0_10_26.exe',
    'DTLBootupHelper.exe',
    'DTLFeedback.exe',
    'DTLInstallProxy32.exe',
    'DTLInstallProxy64.exe',
    'DtlManualUpdate.exe',
    'DTLScreenCapture.exe',
    'DTLServHelpProxy.exe',
    'dtlupdate.exe',
    'DTLWinHelper32.exe',
    'DTLWinHelper64.exe',
    'DumpUper.exe',
    'EditImage.exe',
    'elevation_service.exe',
    'env_detect.exe',
    'ExplorerShell32.exe',
    'ExplorerShell64.exe',
    'FaceTool_2345Pinyin.exe',
    'feedback.exe',
    'ffprobe.exe',
    'FlashPlayer.exe',
    'gamebox.exe',
    'GameChrome.exe',
    'guardhp.exe',
    'hao123toy.exe',
    'hao123uninst.exe',
    'HaoZip.exe',
    'HaoZipAce32Loader.exe',
    'HaoZipC.exe',
    'HaoZipCD.exe',
    'HaoZipHomePage.exe',
    'HaoZipLoader.exe',
    'HaoZipLoader32.exe',
    'HaoZipMd5.exe',
    'HaoZipRename.exe',
    'HaoZipReplace.exe',
    'HaoZipService.exe',
    'HaoZipServiceManager.exe',
    'HaoZipTool.exe',
    'HaoZipUpdate.exe',
    'HaoZipWorker.exe',
    'haozip_000003_v6.5.2.11245.exe',
    'HelperTool64.exe',
    'IeView.exe',
    'innoextract.exe',
    'InstallGame.exe',
    'KuaiZip.exe',
    'kuaizip_setup_v3.3.2.0_kzgw_23.exe',
    'KZMount2.exe',
    'KZReport.exe',
    'LdsDrvInst32.exe',
    'LdsDrvInst64.exe',
    'LiveUpdate360.exe',
    'LoginPlayer.exe',
    'LoginServer.exe',
    'madVRSetup.exe',
    'MediaFileHandler.exe',
    'Miniblink.exe',
    'MiniThunderPlatform.exe',
    'MPHelper.exe',
    'msgcenter.exe',
    'NetmProxy.exe',
    'NetmProxy64.exe',
    'ngen.exe',
    'notification_helper.exe',
    'oauthlogin.exe',
    'password.exe',
    'PdfEditor.exe',
    'PicCompressTask.exe',
    'PicService.exe',
    'PicServiceManager.exe',
    'PinyinService.exe',
    'PinyinServiceManager.exe',
    'Reader.exe',
    'readertray.exe',
    'Recorder.exe',
    'repair.exe',
    'RMenuMgr.exe',
    'RpcHost.exe',
    'RpcMediaDecoder.exe',
    'RunDll.exe',
    'rundll64.exe',
    'ScreenCapture.exe',
    'Screener.exe',
    'screen_capture_helper.exe',
    'SeAppService.exe',
    'service.exe',
    'sesvc.exe',
    'setup.exe',
    'setup64.exe',
    'Setup_hao123.exe',
    'seup.exe',
    'skinbox.exe',
    'SodaClip.exe',
    'SodaDownloader.exe',
    'SodaUninst.exe',
    'SoftMgrInst.exe',
    'SoulDancer.exe',
    'staticwp.exe',
    'StellarCmd.exe',
    'StellarMediaServer.exe',
    'StellarPlayer.exe',
    'StellarService.exe',
    'Stellar_20230208162342_cl_01_stable_full_x86.exe',
    'SWBrowser.exe',
    'tabGame.exe',
    'tools.exe',
    'Tool_Uninstall.exe',
    'TSBrowser.exe',
    'TSBrowserLauncher.exe',
    'TSBrowserLiveup.exe',
    'TSBrowserSvr.exe',
    'TSBrowser_850_6.0.4.2.exe',
    'tsbrowser_proxy.exe',
    'uninst.exe',
    'Uninstall.exe',
    'uninstV3_ForV5.exe',
    'Update.exe',
    'Updater.exe',
    'UpdateTimeDate.exe',
    'UserCenterCore.exe',
    'verify.exe',
    'vip.exe',
    'WallpaperFetcher.exe',
    'WebView.exe',
    'windows-zh-cn-kb971513_e346619c01cd4f7059291d8bcacb4b8579d1aaf8.exe',
    'wizard.exe',
    'WpDynamicApp.exe',
    'WpfApp.exe',
    'WpNotifyApp.exe',
    'WPPluginHost.exe',
    'WpSnapApp.exe',
    'WpTinyTray.exe',
    'XLBugReport.exe',
]

VIRUS_MD5 = {
    "2345explorer_000435.exe": "f2fcfd8eba53548c06dbfb50af7b9d06",
    "2345gamebox_7cc75f8a.exe": "66f1cdad28f4105ff9a2146301a0bd9a",
    "2345OCR_000001_v1.2.0.243.exe": "ab4eafc07a12c1736fa11bd654f9527d",
    "2345PdfConverter_000002_v2.9.0.823.exe": "0064a739867a5cbe1fb3de062cda7bc0",
    "2345pic_000002_v13.1.0.11876.exe": "05e0941ca647b75e53094758df186903",
    "2345pinyin_000003_v7.9.1.8335.exe": "9c42013b21efaf2d114fe1823b6e8456",
    "2345_softmgr_movie_000003.exe": "0c516bffb80ac98fdb9c12070ad97854",
    "2345软件管家8.14.2.14522.exe": "a55968fc6e8bb682b0447ef4b543645e",
    "360DesktopLite_zm000001.exe": "f8d72c58704850932356b8e668db117a",
    "360game5_setup.exe": "3bb8e133d4ea0e57edfdde702a7a7980",
    "360hb4.0.434.0__1003__.exe": "22bc6592a5081e5b78297f169613d81d",
    "abckantu_v3.2.2.8.exe": "cc3012c21829423121af2a1b9c5e0535",
    "birdpaper_home.exe": "f63c512a950093781f51676134dcb22e",
    "DGSetup_Home_KZ.exe": "a22526f1eb3dcb5d16dbc23575dd5767",
    "DriveTheLife_2571_10_0_10_26.exe": "8f382386c3be821da343d41898729757",
    "haozip_000003_v6.5.2.11245.exe": "e56df8b32a17edefb5428bf23e8af475",
    "kuaizip_setup_v3.3.2.0_kzgw_23.exe": "4f73d3ff916bde32f3727f93ade9b11e",
    "Setup_hao123.exe": "8a5465af3a681bc879626c68584636f4",
    "Stellar_20230208162342_cl_01_stable_full_x86.exe": "e4a18a2de51e59d0d4902ee1a8f13072",
    "TSBrowser_850_6.0.4.2.exe": "67c470b99ae84071772012ca546782c5",
    "2345Explorer.exe": "0970d839b3cee8237fa2d8f11bc52f5d",
    "chrome_proxy.exe": "2cd0d12d9e03603aa39ccb2e43b34235",
    "Uninstall.exe": "b0ebe276ab5ec8abdcbc1151c37aa285",
     "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "courgette_dll.dll": "6ef057c9f8a07dc50185b0d669e968cd",
    "d3dcompiler_47.dll": "5ce90e0d97f339e0cdf9873d3cb7c222",
    "elevation_service.exe": "ed9ffd3077228487df2b4d369eb969b0",
    "libcurl_x86.dll": "940c40feb0f6fe025298748f5901930a",
    "libEGL.dll": "0a2134b65df2c8089691957ede4456de",
    "libGLESv2.dll": "5f163f612fa97fe7f511565f940de26e",
    "mojo_core.dll": "13740b1d3c42f211ed5e2efea7c3e13f",
    "notification_helper.exe": "ecb770c29634a280bac8cc1d42953ace",
    "Trident_core.dll": "f6257d1ba91ab63e69cc66ac6b4be069",
    "vk_swiftshader.dll": "d7e9cc90c992eb78f41c1c6e4db5e08c",
    "vulkan-1.dll": "21f3cc0b0f65f2cc69c72ae2fda1bb66",
    "2345Capture.exe": "bc7af507ca5b5d8a3e1c4b80b77fdc23",
    "2345CaptureApp.dll": "be3e4191354d9a91db7c7c568329aa84",
    "2345MgrDLL.dll": "f9b527c0a285bdb9f53e76e85b27ca3f",
    "2345MgrDLL64.dll": "1376ff268e2a998eefd92018da3e32b6",
    "2345Uninst.exe": "f9010c8ea3ef7b23c867361d1b1a727c",
    "HelperTool64.exe": "59e16e0fc98a2b5aa0e4566a776af8c6",
    "widevinecdm.dll": "0a4d5aa895867ba557d108a45de0cbf9",
    "Doctor_2345Explorer.exe": "ab0d9acf223903056efaf872186a6409",
    "AssistExplorer.exe": "7fd02a9a873d353dc72cf5c8b64f40c1",
    "AssistMain.dll": "34ecaaebe3d22e04875f3a741baac9d9",
    "BrowserService.dll": "f123f33e173dfd5b6bd64c59d8aa374f",
    "BrowserService.exe": "e8d7be3f7558533bf04d1469b4c3fdf1",
    "BrowserServiceManager.exe": "401e244377a5ea03ca3de67f3b8119e3",
    "Tool_Uninstall.exe": "d4f0a4fbe3e1c0cb2f725d85a62a0840",
    "2345Desktop.exe": "8ca6d5a0e13cd2f01cc3d5183d3ca923",
    "2345DesktopLoader.exe": "1809907e68988431b5d9f810185e150b",
    "2345DesktopService.exe": "f96bd3d1bc697fe8cc97e5f7cc252051",
    "2345Extract.dll": "30decbbfff805046664241fa45693052",
    "Uninstall.exe": "e19b85b2650e5ffdd686d19264751da6",
    "2345Movie.exe": "daefa6f90959fa491cf9c8d6d98ea55e",
    "Uninstall.exe": "c3d585b2c8ac7344f465a0308cfbd330",
    "2345ImageCapture.dll": "37bbf6b0f346d67bda0fdf816388282b",
    "2345OCRConverter.dll": "14e587027bb6836a986de55e174826c7",
    "2345OCRDumper.exe": "4c2bf4b06300071046d0da9dc5710124",
    "2345OCRLoader.exe": "8e28e1180464c40934c4643368c531fa",
    "2345OCRMain.exe": "6d758bccb02ed7c92d1978e9d9dbebca",
    "2345OCRUpdate.exe": "fdad0c87072f54dd13a0eee27497c786",
    "2345PdfInfo.dll": "e1389887ecfa9a72fd272dc67ffb8e8c",
    "2345Uninst.exe": "f3eb9a969d6294b40977e8992bb1fb28",
    "coral_extract.dll": "4ec504ce7722ecac1897c4b0183721c0",
    "courgette.dll": "41436ed25a63f401b54f42a2b65b3be1",
    "D3DX9_43.dll": "86e39e9161c3d930d93822f1563c280d",
    "FreeImage.dll": "a5086ed43784c02b272abe4c7e161708",
    "FreeImagePlus.dll": "6e7809d3d4379dc28b9082a333c256d1",
    "icuuc.dll": "c6fbf8d028121aa9c0b1fd4b0adf23fb",
    "libcurl_x86.dll": "a26e75c0407c87786eea42febdb32532",
    "pdfium.dll": "33246df62ec8ebf77c5073678aa98a83",
    "ucrtbase.dll": "6343ff7874ba03f78bb0dfe20b45f817",
    "vcruntime140.dll": "1b171f9a428c44acf85f89989007c328",
    "zlib.dll": "8494bacc6359c4315c9947a8d2429c92",
    "2345ImageRes_x125.dll": "bf999ead7141584ad07d7a64c7f3b2ff",
    "2345ImageRes_x150.dll": "dd7267b643228d3c65060edeeb419a1c",
    "2345Pdf_x100.dll": "a0bef5450753408b3cfa675cd34a5556",
    "2345Pdf_x125.dll": "1ea269fcc35d66a05fdff555cf4fe741",
    "2345Pdf_x200.dll": "df7bcec0378c7360c7c46b6fc1c3f57f",
    "2345EditorLang_chs.dll": "058bd5c75d842a5c980045c2a5f504d1",
    "2345ImageLang_chs.dll": "210d77e7a4e4e25e649be0fe0f7474d2",
    "AssistHaoZip.exe": "97386775951a7f1ea061fc0208c5a570",
    "AssistHaoZipMain.dll": "f091f79eb8d1a2f848b71fd7f2652973",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "HaoZipMgr.dll": "f9b527c0a285bdb9f53e76e85b27ca3f",
    "HaoZipMgr64.dll": "1376ff268e2a998eefd92018da3e32b6",
    "HaoZipService.dll": "4b535a42f38340c23abc67b948ef04b3",
    "HaoZipService.exe": "e2f46df6bec6f52ceaf1dbb23c583e1a",
    "HaoZipServiceManager.exe": "346fb49f20ecc4ed096da82ecec608da",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "Tool_Uninstall.exe": "4f7eecc3c6bfb5c7c561db5fdcd085e2",
    "AssistHaoZip.exe": "0bba25319accf81eb295259c227d8e21",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "HaoZipService.dll": "d6946b310def83ee28c88a5be043a802",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "BoxDoctor.exe": "a39cfae0bbfa6be79b88bd801d079184",
    "chrome_elf.dll": "1e143c5bef85048803aef29853c09e24",
    "d3dcompiler_43.dll": "1c9b45e87528b8bb8cfa884ea0099a85",
    "d3dcompiler_47.dll": "f76b1d2cd95385b21e61874761ddb53a",
    "EasyHook.dll": "90415654892f050b9ee8ce0742d47406",
    "EasyHook32.dll": "6acd6c59d4745553bf00d03911691319",
    "EasyHook64.dll": "fb355d3abb3c9fe18d2c846d4d7bf0c1",
    "gamebox.exe": "6bad24f9c80bfd9cf744f8d6877536f8",
    "libcef.dll": "0afbff9a7fe79332e131268154c20871",
    "libEGL.dll": "9a8bb417d0381fc81ed6e91ef23fcfbb",
    "libGLESv2.dll": "7280b7666d9e8f92d7af9b97568573dd",
    "MouseHook.dll": "0b089800520d44cc209892ea9006f9b2",
    "Socks.dll": "c2958e0a78285403dc52d824a7f9b97d",
    "tabGame.exe": "658039245557e8da7fe1e33c94e04c12",
    "uninst.exe": "09f01b4a4db84da72d9e78dff959b4be",
    "widevinecdmadapter.dll": "a83d199f55b6c88a1f402cab913f65b6",
    "zlib.dll": "d0be20f9594398b5f0333ed6813e9bf1",
    "libEGL.dll": "be71d45f21ca2f6c8f0c81cf371b1b68",
    "libGLESv2.dll": "d436b699a89fcf60bf68e563e94fc93c",
    "360Game.exe": "9117bc3582c929cba7f2c5ba7b1e980b",
    "360GameAndroid.dll": "0c15cbe841a46854dbe2b52f06f94b47",
    "360GameBrowser.dll": "ed339943c23483e4e2b9b259e6de43c7",
    "360GameChrome.dll": "559bd189ed05787476373c0bd878d4f6",
    "360GameDB.dll": "8022a8184b93d30868ae1f5254696dc1",
    "360GameDLBridge.dll": "912f167afaefa2a0bef5fab8eefdae10",
    "360GameDown.dll": "96dc3b7da654fe6515590ac4d31addb1",
    "360GameHttp.dll": "da580c9f5a07be749b8e28cee65bae3a",
    "360GameIPC.dll": "b83ea7a4a46c13b2bb9a40a2d7992424",
    "360GameKM.dll": "e9a7a7536b181cf7e000e279004e1549",
    "360GameLauncher.dll": "1a10831cd953cd46c600183e0d2a8885",
    "360GameLiveUpdate.dll": "21c27d27efe11d1faaa829b140d41eb0",
    "360GameLogin2.dll": "d36201dc886569ad94d63eed56bfeb72",
    "360GameTask.dll": "3a5aaaca19841f1eefae7abc845dad0b",
    "360GameTray.dll": "345d61bce36a50d06089a0328251a3ce",
    "360GameTY.dll": "7ce60a1ff776ef9bf84671e1544571f5",
    "360GameV3.dll": "34cbef911f56f6d3716a1b31ce30fdcd",
    "360GameV3Task.dll": "e265fcbbd41a424d39e3f2dea1c1b924",
    "CrashReport.exe": "52f449ab3e1c1f5d7324dc438cfca5df",
    "Dump.dll": "c5f68abb95c663a603e095d8cea3d859",
    "GameHallAutoRunExt.dll": "b2cb93bf5781ca495b66d43902f6a376",
    "hiya.dll": "24c66a1b8c72b4e355793c4d8d8f8dcd",
    "InstallGame.exe": "de13795c2bada01419e2c607b5070457",
    "Screener.exe": "3bad13f2c29d26342a27fd46e55aeef2",
    "sqlitedb3.dll": "52059442b64db181cfd9ae0a2a64cbbc",
    "uninst.exe": "77afc45ee1874b17a4d7f8b9108872a0",
    "uninstV3_ForV5.exe": "68c27a17fed765d23339bb7434c2e542",
    "windows-zh-cn-kb971513_e346619c01cd4f7059291d8bcacb4b8579d1aaf8.exe": "d1221255a9642ed681561cbce5a50856",
    "zlibwapi.dll": "dd425d3b1e9b628875b3841ba8b85f56",
    "360Base.dll": "2f9fe542b5f9812d1d4dc56736bf903b",
    "360Base64.dll": "c9c185959497d52f5de54dc8d12b1df4",
    "360net.dll": "67102ccd7809e2f0618110ef6f91d339",
    "360NetUL.dll": "cd03029957ebc78c0ca7a6c02a9ca846",
    "360P2SP.dll": "d47bb1ada6dcd905a47875af0ed5294e",
    "LiveUpd360.dll": "9ab71c60f691691686fa2cf68f2bd7aa",
    "oauthlogin.exe": "8c742e6ffc84ad9a2258aabbd9dbda8a",
    "PDown.dll": "7519d09cbf88ce690d3a6a11187d6e2f",
    "safelive.dll": "6b4c1a58dbb9a25578d89521d5d28fce",
    "aapt.exe": "81d2c6bc1a3868d47e1ed78b8746523f",
    "adb.exe": "0259b5c3ebf708a0ecf54b846ad05828",
    "AdbWinApi.dll": "47a6ee3f186b2c2f5057028906bac0c6",
    "AdbWinUsbApi.dll": "5f23f2f936bdfac90bb0a4970ad365cf",
    "360Game.exe": "b8615d0bc2b59cb84085ffec226c3b37",
    "360GameIPC.dll": "de34d7399be1fa102578d8e6e9c568b2",
    "360GameLauncher.dll": "6ddceb83850096289589c02968ed3f35",
    "Dump.dll": "5c1a27c7226519c994883c2606a40738",
    "xldl.dll": "40e8d381da7c2badc4b6f0cdb4b5378f",
    "atl71.dll": "79cb6457c81ada9eb7f2087ce799aaa7",
    "dl_peer_id.dll": "dba9a19752b52943a0850a7e19ac600a",
    "download_engine.dll": "1a87ff238df9ea26e76b56f34e18402c",
    "MiniThunderPlatform.exe": "0c8f2b0ee5bf990c6541025e94985c9f",
    "minizip.dll": "7fd4f79aca0b09fd3a60841a47ca96e7",
    "XLBugHandler.dll": "92154e720998acb6fa0f7bad63309470",
    "XLBugReport.exe": "67c767470d0893c4a2e46be84c9afcbb",
    "zlib1.dll": "89f6488524eaa3e5a66c5f34f3b92405",
    "chrome_elf.dll": "e89260d68ff566c6126b755b5a6a0340",
    "d3dcompiler_47.dll": "044fbeb37053ca2d62f85ef79da706e8",
    "libcef.dll": "226796dc783009731bf0cd9456bdcf42",
    "libEGL.dll": "d880f45c34b7748b7652a51104c6bfbc",
    "libGLESv2.dll": "a091cf03a1bc1d5f3c66ef186d427294",
    "libEGL.dll": "66c02b485abafe580a7f64db734e4fd5",
    "libGLESv2.dll": "2dbae2378469a43cfe9b41ddba76bbf3",
    "360base.dll": "a73cf0457df35fab74ef3393d2766667",
    "360huabao.exe": "0e00e47461fa1a4e1121bd057dbc5aab",
    "360huabaosetup.exe": "4af92010ee63d940158d9d5ba55f1dc4",
    "baseutil.dll": "297f8e05d26092feb32fbe3d7cc8a0a0",
    "HuabaoUtil.dll": "dbb503d62f77b9e3d36318b17c98e5f4",
    "360Base64.dll": "c9c185959497d52f5de54dc8d12b1df4",
    "360hbtheme.dll": "45e08ec879f207bfc2ceac04682c8b07",
    "360theme.exe": "ff8904c1b0486e4d595015e79bd63e91",
    "AndrowsInstaller.exe": "115236fd9e6bd847b65199e2d70ac75c",
    "env_detect.exe": "e88f0ac61bc1e762c4a60f0486746ac4",
    "ocean.dll": "5684123f4fe90b0872335959d93ed6f5",
    "pcyyb_sdk_dll.dll": "5d38d41c99c8431c83065e8b34db5853",
    "qimei.dll": "bccc4863524b6931716db4686ad424d7",
    "qone.dll": "044c8dc049f0ec593e66a1e027071cf7",
    "3d6tDll.dll": "632cef37d1bc8b7c84ff106eec9d20bf",
    "MPHelper.exe": "a9f31011bf4a8ddc3d51f3d33486d84e",
    "360Base.dll": "4f241e5de9091f6d78469bf1dc141cbd",
    "360Base64.dll": "497c4af8579ed8c58ece77d8cd2bdffb",
    "360Common.dll": "4fc0b14d968a2e48201c87ef03af07b7",
    "360net.dll": "93779ad3d7a16ba57e879e97c51887f3",
    "360NetBase.dll": "14c6b4bbd31f6fd13530bc941cc71d1a",
    "360NetUL.dll": "2586f41adfba6687e18e52b75f69c839",
    "360P2SP.dll": "bbae3f09aed15103df0c9e3cf5e2ce00",
    "360Util.dll": "d1b5dfc13bc47b666d0bffa3520d4c29",
    "360办公助手-AI文档处理.exe": "c4fa8404404df6f6a8c12237c0f11eda",
    "CrashReport.dll": "a1015b3bd68bdcf4627decca879685ee",
    "DumpUper.exe": "a223839a1dbe1dfeae57dd67164f31d8",
    "LiveUpd360.dll": "960b05116f13ae8e8b17a6ba2919bf2d",
    "LiveUpdate360.exe": "7ab1039a906d85c00d8b83f10f374340",
    "LoginServer.exe": "a365e80fbec530496e4570d4e7743616",
    "MiniUI.dll": "5123c3b8adeb6192d5a6b9dc50c867b1",
    "PDown.dll": "637fb39583f9c2ec81e0557970cd71ad",
    "Reader.exe": "d91491977fdbc6b74602e2e34a409d4d",
    "ReaderCore.dll": "608f7cf8a88470aa9301c494a173baaf",
    "readertray.exe": "4357a4a0a712bf309def836efaf702ec",
    "sites.dll": "3f03f2c6000d713bf0c2824eb6021fe7",
    "Soda.dll": "e2927be696866b484f7207652cc1a45f",
    "Soda64.dll": "ed393cf44b0daa49d4fab3788275fd02",
    "SodaDownloader.exe": "72858ba42b8f1d91a879704ae46cd686",
    "SodaUninst.exe": "d67161a65b762d5ee368b2bdea60ea99",
    "SuDaExt.dll": "c55c61be57739320f837086b8e6197b3",
    "SuDaExt64.dll": "234b26278c244d005734aa79255cd41e",
    "360SudaExtInstaller.exe": "671f1f4efd22c26fc5e54f181495a94a",
    "360SudaExtWin11.dll": "597ecd4306de4aaca407419b931a2ef9",
    "360CloudApi.dll": "4e19ad0a505457176fdf529edf2d6d24",
    "360DesktopBackup.exe": "20f86f29316656938f5eeaff030f79d6",
    "WebView.exe": "fbf0ec7447d15526f879afdebc560597",
    "360AlbumViewerUpdate.exe": "0aa8b3d090f36813800e6732e69c6872",
    "360Feedback.exe": "3608cf45dd3c6dd93e4e331bd83df6e5",
    "360ScreenCapture.exe": "f3267294f05be72d697107cb92a429c7",
    "SiteUIProxy.dll": "d1d324087da908c44194edc103def1cf",
    "SodaClip.exe": "3cef8e4a02966a71076b5353b35bfb45",
    "360secore.exe": "ab8434b44b66a2920b39dd01061621aa",
    "360base.dll": "a73cf0457df35fab74ef3393d2766667",
    "360bdoctor.exe": "a224495e8941263bc1f37e211d1dde76",
    "360seupdate.exe": "ca3f3cfbf05986b395b2e127418c5d96",
    "audiomute.dll": "008d9c0298fac86bfb668a9f2aabd73d",
    "chrome_child.dll": "27f2eacf71f1373fcb32f0fd4087a306",
    "chrome_elf.dll": "cae71b48ee4856b33c98e0e389c6a02e",
    "commlmgr.dll": "b7ff514f693cd1121e704a81d1c8f49c",
    "d3dcompiler_47.dll": "3b4647bcb9feb591c2c05d1a606ed988",
    "KitTip.dll": "94108b412e846c6e85aee79cf66c15bb",
    "libEGL.dll": "1c69ef32f97f3da116d89515a4cfd689",
    "libGLESv2.dll": "eb082dcb78c28f3ce87915ea6172635f",
    "libx264-148.dll": "85c04b28e77083f1fa3c6dbf5af1a010",
    "MobileAdapter.dll": "2a5ae50b13861b98a5c4ce30eddd90ab",
    "NetmLauncher.dll": "0c03fb883dc33b87f22911bc7e89f034",
    "NetmLauncher64.dll": "42ca2386dab754ca5ec068da5de68773",
    "NetmProxy.exe": "f0274b1f795e7f425a180fb210ab2b6f",
    "NetmProxy64.exe": "b6098de8baed9ead05827a57ff5cc08d",
    "NotifyDown.dll": "dd49ce0656c611bdf74471b248a1d1a0",
    "presetui.dll": "4d7dca49ed98a9d22d36dbb535a779a4",
    "safe505.dll": "631c46619d31f985225c68a4fa2770de",
    "seapp.dll": "a1bfe129350f5c8cdc8eb1171ceaec1a",
    "SeAppService.exe": "2e311598b7f6a37d8fab1eac4e374c0f",
    "seregedit.dll": "8114cd38d793499483a2c17a77d475e9",
    "sesafe.dll": "eb22708072bac4d697390aeaa1943e22",
    "sesvc.exe": "2c03a088492816f5b272c307f482e60f",
    "setdefbrowser.dll": "528670c09f6917aac86c86f21bda0295",
    "SeTrayNotify.dll": "001cdee2049e786c1cdac2aa762cf354",
    "smartpreheat.dll": "9927981fbb2d85552c313e91e1ab5369",
    "smartpreheat64.dll": "fb05cfada19b742db830f5803fca9bad",
    "urlproc.dll": "b2d2c6582fb2dac307b8e6f6bfb8d5c8",
    "vk_swiftshader.dll": "c95a4f1967e8cc423775fe882baf11a0",
    "vulkan-1.dll": "f1dd1784cb15abf1c220b318d60af57b",
    "360FeedBack.exe": "fbdfb250504236015f453b053ad572ec",
    "360chromeup.exe": "215996735192e41015be9cef3c8b6caf",
    "360ini.dll": "fd33b0dfbc35f3da4b7425b9b196d1cb",
    "360net.dll": "d5f22fc1beff60f5fa9398effca73e2f",
    "360NetBase.dll": "0cb01edeb737f50c9263f697c136e450",
    "360P2SP.dll": "bbae3f09aed15103df0c9e3cf5e2ce00",
    "360se.exe": "04a433fb9a29275cbfccda52cb1dca90",
    "360secore.exe": "ab8434b44b66a2920b39dd01061621aa",
    "chromeup.dll": "27711b36eacddf254c6cceaf9c2c954b",
    "CombineExt.dll": "daabfb8e3d5b00a465532da5d6a18850",
    "InstSafe.dll": "368146e3189ff96d303545c933d2ef35",
    "LiveUpd360.dll": "4d2f0f48ef41c9e663bf418aa95b47c7",
    "PDown.dll": "15dd99d64a37791706fdc141b7ff7c25",
    "Safelive.dll": "a173cfd976193616bd709c4fa4b507d8",
    "setup.exe": "931d03651e7ad0146ec5cf0d9e71b552",
    "setup64.exe": "39e25fdcbc0fe52d96da002d453561fd",
    "seup.exe": "28fb8b23667c520e9c85351cbd80ed57",
    "360wpapp.exe": "b92a18de1427b9ce3b99aa8817f78152",
    "360wpsrv.exe": "668ce5e9c7eeb44bd08c95b04fb3d922",
    "Base.dll": "f58a212ed54c642b73df5b3fc9926b05",
    "Base64.dll": "3e3fd2ef99ac4eb3efce6fc9a27c6ad7",
    "birdsrv.dll": "8265e9c8b6bad14eae214e9f905965c0",
    "birdsrv.exe": "668ce5e9c7eeb44bd08c95b04fb3d922",
    "birdsrvhost.exe": "a0b284eab96ae959ea008c12f174e8bf",
    "birdtray.exe": "dc5c0709481142425e75d1259bcbee1f",
    "birdupd.exe": "a0667ebe610698de3606bc9aefe4bfcd",
    "BirdWallpaper.exe": "a3fe6fd062772ca8cec27d0a8f1f3820",
    "birdwp.exe": "148e245d188f1a984741638d130ca2d1",
    "Common.dll": "dc3d5e741ac4000a4d0267ef4562533a",
    "MiniUI.dll": "7ae7c94c2d28bc98d1d5b8d546968747",
    "NetBase.dll": "b0401b8c27efab04e7e5ca841f0f928b",
    "NetBridge.dll": "aa58690f40ef0acfce30706e5fc201b0",
    "PDown.dll": "91882759c8a8f06b70f8e471bc730df5",
    "Safelive.dll": "e8187cd396148baf0c7b472f7ee79efd",
    "sites.dll": "720ead856435c7a1345f844e90b478f1",
    "Uninstall.exe": "061ddc7f32c6b15b44437167a1831f67",
    "verify.dll": "b26d89f1440c500f4275f4d2c64d64d0",
    "WpTinyTray.exe": "bf68c9e6f689f497dba9dd041e24de4e",
    "avcodec-lav-57.dll": "3fb3c5af7d6c4db3c9dcfc5d3bdf707e",
    "avfilter-lav-6.dll": "71d2fc9029be8e50e967c9eb0d0ba7a4",
    "avformat-lav-57.dll": "dda9f3ae25c4bba1251008d24aa317f7",
    "avresample-lav-3.dll": "78798a3320e1f20174d5d53b3b50e297",
    "avutil-lav-55.dll": "70496aa3fb6d1ed958092c99edaaaaa6",
    "BirdPlayer.exe": "2973df32541971b024eb29ed14a1cacd",
    "D3DCompiler_43.dll": "1c9b45e87528b8bb8cfa884ea0099a85",
    "d3dx9_43.dll": "86e39e9161c3d930d93822f1563c280d",
    "DynVideoPlay.dll": "bba516ad382e2529d89ac87d4e9dc7ec",
    "Dynwallpaper.dll": "2ba987007f6132e5569fd4c2cc84907f",
    "DynWallpaperService.dll": "4a06c52f025a2017c4a0d1624e6c6827",
    "libbluray.dll": "9c5c1cb5ad1a4781c40775eb94561fa7",
    "SDL2.dll": "ec15b044a46bf6e411f9eba551858030",
    "swresample-2.dll": "610610749f6f3aad217cc75eece9f349",
    "swscale-lav-4.dll": "5b103ab86429c2af4ef299db94e418e4",
    "ModeIdentify.dll": "0cd03ad8a94e3687968a02e2576fa408",
    "GmSvc.dll": "5d121c5e456f4a61fc9d62f3bf237e62",
    "WpSvc.dll": "0d1d1a520071ca29b81161d930ac8185",
    "WpSvc64.dll": "daaf1e8726e40f1267bc79d022dc2d8f",
    "ConfigCenter.dll": "a5f30b9681859aae5baaa1cd96825bf1",
    "ConfigCenterStub.dll": "2f12805c6c7ef7c43272f52c4beee243",
    "PopMgrStub.dll": "2f053d678e0aa372f2046e473b9ee938",
    "SoftMgrInst.exe": "447e5dad44daa767c71e0ec766e52f0a",
    "arctrl.dll": "8cdbb3c5ee56020a7c099908524f5950",
    "BirdHelper.exe": "c6b6c23ce0657b3fd1941a45d582629b",
    "BirdRecommend.dll": "48128c1c0385b2f2738a8f38ec95001c",
    "CefHelper.dll": "d119629c5bd9b5329ab0d4023e042190",
    "CefRes.dll": "fb24a5c769016510c13d40685a3d90f5",
    "ComputerZ12.dll": "65536a3888b476db7394a8f30df33905",
    "ComputerZ12_helper.exe": "635d95024a8d2d04ecd4baf0ad41c666",
    "ComputerZ12_x64.dll": "a938d0d5d92c01824c68b5d1fc88120f",
    "deskicon_coupon.dll": "e2a092b23d2547bd27c72f75ec6bcf86",
    "DisPatchMini.dll": "59edf9028eceb1aefefccc4cbe3c573a",
    "Down.exe": "b9d9fde7b77244297f4856cc7a81dba9",
    "DumpUper.exe": "a3c40aaad2cbe9380696182d88ac8a1c",
    "guardhp.exe": "f431b9d5fc20cd8669b9b9b75d57821d",
    "heifconv.dll": "33993804b5619a4818c448ce95da53a4",
    "hp_guide.dll": "99d3a5f049d967ce4f892531ebf8854c",
    "LDSBasic.dll": "7d7ac0138d7c7b52457ab6ec2d5497e7",
    "LdsDrvInst32.exe": "d17ba76ab7585131dfeb1e342ff24e93",
    "LdsDrvInst64.exe": "66c3a6807506651713ddf2789256ee0b",
    "LDSShellExt.dll": "18aa67a69e12780eeedc851436571b98",
    "LDSShellExt64.dll": "99168897f1dcbfe4ce4fd551044b616a",
    "LdsVolumeCtrl.dll": "5c6a3ba2d7f3df29664130df5295d4aa",
    "LockScreen.dll": "05ba26a75d4bc5f265553cd204a3ed77",
    "netul.dll": "7ce0f64517771c3f89ee0c21e55b174e",
    "pg_recomm.dll": "857bb8bd33c28966435fa95be514a87e",
    "Pop.dll": "6a60b6614c8bb2d0359ebff44acbdf19",
    "PopEx.dll": "44096fd33b99dd292fd40b3e28285ec2",
    "RunDll.exe": "77b725d6e835b9f8f3e01ca43fa4d0e2",
    "rundll64.exe": "05502d2ef09218b7a20a951958a608ee",
    "SiteUIProxy.dll": "d1d324087da908c44194edc103def1cf",
    "SoulDancer.exe": "974e3f993671789b7fccfffcc38ed3bd",
    "staticwp.exe": "de2321708a826a6b05ef194ff1787bd2",
    "WallpaperFetcher.exe": "447e5dad44daa767c71e0ec766e52f0a",
    "WebView.dll": "402235119134f454ce6ad020f6bdbc62",
    "WpDynamicApp.exe": "18f52605fe6a00839c41af3a2df6e44a",
    "WpNotifyApp.exe": "7b456eb609b48817992bf6ecff2e65e7",
    "WpSnapApp.exe": "570a38edbbe3272f3c5b98488578161a",
    "BeautifyExtension.dll": "17acfc4ba87d33f9b4698a5b64267ef0",
    "BeautifyExtension64.dll": "a8da2261fe7d44aa261e9f44dddbd154",
    "BeautifyProxy.exe": "7c260d3f65a775c82edad5e3832b2492",
    "BeautifyProxy64.exe": "0f8c9d91814583626fa1966b89c988c8",
    "DeskBeautify.dll": "6ef5348f5b8d0d1ddc38d74e310fe2d1",
    "ExplorerShell32.exe": "b4c99c4c727ad8f1723f0829c83af9eb",
    "ExplorerShell64.exe": "29e6aede437ca6163e3993022474b7d2",
    "ExplorerShellDLL32.dll": "610af2c29a08a4c9a38b88eebf36d32a",
    "ExplorerShellDLL64.dll": "2a5efdb92356b4bbc77ea58ded99da24",
    "CefView.exe": "ccdf342378f3071ecb40d335be0c03aa",
    "chrome_elf.dll": "e85ad1cfa89313149ef365742e2f9d46",
    "d3dcompiler_43.dll": "5986b0f940483cb6d6ade5fb583b14dd",
    "d3dcompiler_47.dll": "c57f5e934d5a6fb731109449b3f2a19f",
    "libcef.dll": "c0d6a8e4bae9f5288471fc11f649c222",
    "libEGL.dll": "17b6a73b720b0b2492f72afc0513012e",
    "libGLESv2.dll": "5b71f9369a8fa22738dd4ee0041fcbea",
    "libEGL.dll": "d3f3352d0e42eb4e51672f64d3d4a933",
    "libGLESv2.dll": "ee6a86f290b5d7878fc2f69c156d433f",
    "IeView.exe": "28541011317cebdbb1e381e97732b975",
    "NetUL.dll": "0d5116399c9c6a294425cd41440ce0a0",
    "360Base.dll": "f8c6e30aa708e867199a732cc46eb7bd",
    "360Base64.dll": "1fd1c4bea0ce66903b22838fcd03a786",
    "360Common.dll": "24b027ec1f895a84fa9766412abaa20a",
    "360Conf.dll": "b98a1e65f209fe1f10f8564dec0f0c42",
    "360DeskAna.exe": "9c914da5ba91ec1854effa03c4ef6b27",
    "360DeskAna64.exe": "4b26b4b4f38fee644baccefc81716c6c",
    "360DesktopLite.exe": "255a3e02354d080001aef65dba2ebaf8",
    "360DesktopLite64.exe": "cc1802a9fb9b2bc7573b6063d1861efa",
    "360DesktopService.exe": "d515c0ad919755107aa1d39c92d36a04",
    "360DesktopService64.exe": "e628c751652a9e5d20cc1e19993c194b",
    "360NetBase.dll": "ea1ddee32bcc413067a5799c17edea61",
    "360NetBase64.dll": "7bab0d80a6da1ed88b3bd87a8675a27b",
    "360NetUL.dll": "2586f41adfba6687e18e52b75f69c839",
    "360Util.dll": "5dbc4302c1a0865f554d2416c36af299",
    "360Util64.dll": "dd5fcd6b10226a3190dbcd64fcaabb70",
    "CrashReport.dll": "361ee0170374127e396e7ab4d839bdb3",
    "CrashReport64.dll": "8f6bc80e4729bcb792eecaf89e38965f",
    "DesklitePlatform.exe": "f98f4eb1f17dd641163565c27e182a20",
    "DumpUper.exe": "f0cadc9e252dba063209310f5b447ce7",
    "KitTip.dll": "1fa51e2e1c4df3708cdb16c1a7b8440c",
    "MiniUI.dll": "481ecdb043ce58b0ef60b1eabb30f9f3",
    "sites.dll": "2338e0676377401e41b4780c79969a9b",
    "sites64.dll": "88702b9bf529c7e51e017d6901e5863a",
    "SodaDownloader.exe": "a7e873022acddb55e4922e2a75c33769",
    "Uninstall.exe": "161643b2522401eeb0a1baf0bea34a37",
    "WPPluginHost.exe": "8abbfcf074fd5d2f32c7b40a70bfd64c",
    "GameChrome.exe": "38c44c8b2b0c7b3bc67d607b88829daa",
    "360FastFind.dll": "1d0b055daf32c7161bd1c5bfc2c0d1c9",
    "360Feedback.exe": "c6738911dddfa2b7bc5b25f1cc5957c0",
    "360ScreenCapture.exe": "835ebd41af0df047223a0aaf1e9a5556",
    "360searchlite.exe": "67a089a0c8ec40608d90b889cd972871",
    "SiteUIProxy.dll": "d1d324087da908c44194edc103def1cf",
    "difxapi.dll": "f423ae432b719690c74b9a07da6127e2",
    "DIFxAPI64.dll": "1a2e5109c2bb5c68d499e17b83acb73a",
    "DriveTheLife.exe": "6e5c6796422c5145ada2c8f8257175f8",
    "DTLBootupHelper.exe": "7a4dfc56aa0d6bac7d2767e7523f865e",
    "DTLDeviceCache.dll": "333428bbb2ccb967ad50f7b07f3a72e4",
    "DTLDriverBackup.dll": "20e9311b62a2948f3bce450ba5926833",
    "DTLDriverCore.dll": "2fa14313ee5c19911c891a155b7f2915",
    "DTLDriverInstall.dll": "09cc67fd09a738f1f7b4d7824684dfb3",
    "DTLDriverSearch.dll": "273188083afc2e8b644ec91c7ec9f82e",
    "DTLDriverUninstall.dll": "e92ae0a84958a7a376461c0f90329cec",
    "DTLDrvSvc.dll": "532b7d40a6d852c6c22e62b7d637f2c8",
    "DTLFeedback.exe": "e84783abbb24a25ae4a4ddd2e7ee08f0",
    "DTLHWStatusCore.dll": "6624448cdc3f034d6e03a1ff8a392d94",
    "DTLInstallProxy32.exe": "707f88e4bd2dd60450785fc6a6766080",
    "DTLInstallProxy64.exe": "536586a357a68f76d5152a3016708b5c",
    "DtlInstUI.dll": "f0a89633c2d2f7ff7c7643fa37803245",
    "func_helper.dll": "28fa5637e71f38e40a1e0003c1049ae3",
    "TSBrowser.exe": "427dc41009a8705a2ea7003859a5d3b5",
    "TSBrowserLauncher.exe": "71e110f0199cadea0f559b3890aa599f",
    "TSBrowserLiveup.exe": "6d3c6799570fbcbf7f805bf117d62e81",
    "TSBrowserSvr.exe": "575677561c3ee5998304923ba1bf37f0",
    "tsbrowser_proxy.exe": "989875ccaf3f6b263104cb3a4cf691b0",
    "uninstall.dll": "b41063f1ff1ab56f24461704f9f4eef9",
    "Uninstall.exe": "e2cadb5f1fd566a21782100a58314bda",
    "chrome_elf.dll": "8504c72fc9283f66548ade5c10385c99",
    "d3dcompiler_47.dll": "ab3be0c427c6e405fad496db1545bd61",
    "easy_detours.dll": "94ca8e3d31a428bfa2983f0ce3461a92",
    "EditImage.exe": "b20b0447d1df7d2f7bbb3b43c52e96f2",
    "experience_optimizer.dll": "dd2f8af62da6e16c8e306fda4bcc9fc4",
    "libegl.dll": "fb515e8b0040701ad88c701378421897",
    "libglesv2.dll": "abf2db8df4739a6f8a508f143f4b120f",
    "mojo_core.dll": "93c4aea3e50727a679d7d481c577279c",
    "notification_helper.exe": "363cbe0e6b8a94ac86c4e07c15f3dc9b",
    "pcid.dll": "633a510c31f9743b674e4c60c99b1cc5",
    "shdoclc.dll": "6adc0343d1fcaf34f29a759c8580a804",
    "substat.dll": "d9263b0d4862e2cb230ca66379604e97",
    "tools.exe": "cb290b8d30bef57c42d850a0bee4de60",
    "avcodec-58.dll": "ce82b9f0803687490fa0cc20e1aec276",
    "avdevice-58.dll": "c1998ba424d2b5faf0c9925c8c674abe",
    "avfilter-7.dll": "98ca6d894d00b1938c11dd8ee5461dca",
    "avformat-58.dll": "437ab372081d5179f0d1e796362beb08",
    "avutil-56.dll": "413a80bdb937aed8a1cc9a3fddc18cb5",
    "d3dcompiler_47.dll": "a8301cbdc3181b3ef89fc51fb2eddd30",
    "libcurl.dll": "2899b1ace0ea34398203e6428a5ba136",
    "libmbedcrypto.dll": "c17a68c93ee16553bdafb61bb2f2147a",
    "libogg-0.dll": "2da734a56d2e727def8cc9b6618e0dce",
    "libopus-0.dll": "428dff22770ecdbe233cfb6b189722b4",
    "libsrt.dll": "29f5a4b08573e88452377324c0450c0c",
    "libvorbis-0.dll": "514e09aa917800cac771305c76e793d9",
    "libvorbisenc-2.dll": "f9318c526e52809fa71d296949df44d3",
    "libvpx-1.dll": "68f6637e69d11f384bcd10e725d534e1",
    "libx264-161.dll": "7fd3c928bddb4d3b0bca42c34dfb6663",
    "Recorder.exe": "5e415829e9abf67ee95a2f5afc3b771d",
    "swresample-3.dll": "a11d1ea7b1ec897c2c9222a0bab8463a",
    "swscale-5.dll": "e6e588863e57757d938802a616a434bd",
    "ucrtbase.dll": "26b7a7657e4b9658a1dc94439d35dd96",
    "vcruntime140.dll": "a554e4f1addc0c2c4ebb93d66b790796",
    "w32-pthreads.dll": "c756a70cf04233e965816ed39fd60807",
    "zlib.dll": "a0879199c31df08c078c92860497124d",
    "coreaudio-encoder.dll": "fd855e158af393387b3e89a2840c1c8f",
    "enc-amf.dll": "e608e9b0ac3b689ed152e1582aa8c6cc",
    "image-source.dll": "b66e29b66b8fd6cffe6db19ed3076b5b",
    "rtmp-services.dll": "e9f91916d9ede7b0f7ea534186f5d56b",
    "text-freetype2.dll": "a8aa0b6d920470f2191259158996304b",
    "win-capture.dll": "87909a2f3acf369c3e131ad896cca223",
    "win-decklink.dll": "c412934a0f2cf9c1827c4b2e91264df5",
    "win-dshow.dll": "851f9cf3bcd0755161e86103eecda415",
    "win-mf.dll": "117ad112cd53c70738f7287aa57aab3d",
    "win-wasapi.dll": "f57a70a6c70de64de93741dcb3e18968",
    "imgdecoder-gdip.dll": "f666b74be81c5c294777e8fd33ecfd94",
    "render-gdi.dll": "533a317fb6d2e485f76341c4ec807209",
    "ScreenCapture.exe": "59365cefaf409baf3c4de07100684aaf",
    "screen_capture_helper.exe": "90f9898c3ea797e175b56862eb768abc",
    "soui-sys-resource.dll": "6b17e1256ee8d4a6bcd2781c11a38620",
    "soui.dll": "c5cc69e4424241f4bed1ef80b6cf546e",
    "utilities.dll": "870876b906891abd871c99c9b062c72a",
    "libegl.dll": "a333bdd48804314eb82748bbcbc04cbe",
    "libglesv2.dll": "64420ba74b52e8ced1a009adbee04aac",
    "widevinecdm.dll": "f634756cf6a4be877fc71120738ac7f3",
    "KuaiZipShell.dll": "85fdc85ac97988c81be531cd88093841",
    "KuaiZipShellProp.dll": "ff7cd9af1948c1ed41af51c63d9dfff6",
    "KZFormat.dll": "08b0fe1a0bc63c5e6d182aef3f2d255c",
    "KZModule.dll": "aa44c0f986ac24973c12a0822ea8a706",
    "KZMount2.exe": "62e174b2f98b67f1b11d1b49f37e8bb8",
    "Mount.dll": "823cc07c6bef659ea50e2cda5d03d809",
    "MountCore.dll": "b770a7db48d4e1bc784800d79bf5cfcc",
    "Chs_Lang.dll": "6d3acee609f03742b25a9c090779f58f",
    "feedback.exe": "418ffc8e349ad61488e7b137cb5039bc",
    "KuaiZip.exe": "a1ae21f0d7d8634326abfa80f649660f",
    "KuaiZipShell.dll": "d64845da9d930df5f1292ff9afc6e475",
    "KuaiZipShellProp.dll": "96c332b24348ad7f0df0de5d2f885de0",
    "kuaizipUpdateChecker.dll": "dae50ae306dccf02a42e220b2e992263",
    "kuaiZip_dll.dll": "45af291322c84a79f4fda5daff4826dc",
    "KZFormat.dll": "8999fbdc6e17ff0bb1fa2dc0166de46e",
    "KZModule.dll": "0f0dc737bfdc5cfaaf638a46afd01ce4",
    "KZMount2.exe": "60d886d755c41b2ead4e280a7648c6ed",
    "KZReport.exe": "a665a200f778d746443663d2489fcc44",
    "KZReport_dll.dll": "fe0c36028a9c34753748c1a51dc55109",
    "Mount.dll": "8ccd7713b3938e947cb2aaf0e83dd6cc",
    "MountCore.dll": "05bab37f53557a6463752fc6f6c1e854",
    "password.exe": "98a97880fb20b8df06a58b0bca6825bb",
    "repair.exe": "5d08150c0953ed46886c08dcc9d74ef6",
    "service.exe": "18470c6f100d953bbc522fbe443a9c31",
    "skinbox.exe": "1ccf86b43dbe49a715804b9c3ea486dc",
    "uninst.exe": "b0b63c1e59bb965a0f11d14663e1b284",
    "Update.exe": "e96be5faa920d4da52e04645c66a6e91",
    "verify.exe": "822a42add144782bc944cf9ec749199d",
    "vip.exe": "3b23dfbf43285c9d3317e8487d2e1677",
    "wizard.exe": "0142ec7366f3310b40f946b025da5e96",
    "Chs_Lang.dll": "02dee484ae3e3574349da0667a2a9db2",
    "func_helper.dll": "28fa5637e71f38e40a1e0003c1049ae3",
    "TSBrowser.exe": "427dc41009a8705a2ea7003859a5d3b5",
    "TSBrowserLauncher.exe": "71e110f0199cadea0f559b3890aa599f",
    "TSBrowserLiveup.exe": "6d3c6799570fbcbf7f805bf117d62e81",
    "TSBrowserSvr.exe": "575677561c3ee5998304923ba1bf37f0",
    "tsbrowser_proxy.exe": "989875ccaf3f6b263104cb3a4cf691b0",
    "uninstall.dll": "b41063f1ff1ab56f24461704f9f4eef9",
    "Uninstall.exe": "e2cadb5f1fd566a21782100a58314bda",
    "chrome_elf.dll": "8504c72fc9283f66548ade5c10385c99",
    "d3dcompiler_47.dll": "ab3be0c427c6e405fad496db1545bd61",
    "easy_detours.dll": "94ca8e3d31a428bfa2983f0ce3461a92",
    "EditImage.exe": "b20b0447d1df7d2f7bbb3b43c52e96f2",
    "experience_optimizer.dll": "dd2f8af62da6e16c8e306fda4bcc9fc4",
    "libegl.dll": "fb515e8b0040701ad88c701378421897",
    "libglesv2.dll": "abf2db8df4739a6f8a508f143f4b120f",
    "mojo_core.dll": "93c4aea3e50727a679d7d481c577279c",
    "notification_helper.exe": "363cbe0e6b8a94ac86c4e07c15f3dc9b",
    "pcid.dll": "633a510c31f9743b674e4c60c99b1cc5",
    "shdoclc.dll": "6adc0343d1fcaf34f29a759c8580a804",
    "substat.dll": "d9263b0d4862e2cb230ca66379604e97",
    "tools.exe": "cb290b8d30bef57c42d850a0bee4de60",
    "avcodec-58.dll": "ce82b9f0803687490fa0cc20e1aec276",
    "avdevice-58.dll": "c1998ba424d2b5faf0c9925c8c674abe",
    "avfilter-7.dll": "98ca6d894d00b1938c11dd8ee5461dca",
    "avformat-58.dll": "437ab372081d5179f0d1e796362beb08",
    "avutil-56.dll": "413a80bdb937aed8a1cc9a3fddc18cb5",
    "d3dcompiler_47.dll": "a8301cbdc3181b3ef89fc51fb2eddd30",
    "libcurl.dll": "2899b1ace0ea34398203e6428a5ba136",
    "libmbedcrypto.dll": "c17a68c93ee16553bdafb61bb2f2147a",
    "libogg-0.dll": "2da734a56d2e727def8cc9b6618e0dce",
    "libopus-0.dll": "428dff22770ecdbe233cfb6b189722b4",
    "libsrt.dll": "29f5a4b08573e88452377324c0450c0c",
    "libvorbis-0.dll": "514e09aa917800cac771305c76e793d9",
    "libvorbisenc-2.dll": "f9318c526e52809fa71d296949df44d3",
    "libvpx-1.dll": "68f6637e69d11f384bcd10e725d534e1",
    "libx264-161.dll": "7fd3c928bddb4d3b0bca42c34dfb6663",
    "Recorder.exe": "5e415829e9abf67ee95a2f5afc3b771d",
    "swresample-3.dll": "a11d1ea7b1ec897c2c9222a0bab8463a",
    "swscale-5.dll": "e6e588863e57757d938802a616a434bd",
    "ucrtbase.dll": "26b7a7657e4b9658a1dc94439d35dd96",
    "vcruntime140.dll": "a554e4f1addc0c2c4ebb93d66b790796",
    "w32-pthreads.dll": "c756a70cf04233e965816ed39fd60807",
    "zlib.dll": "a0879199c31df08c078c92860497124d",
    "coreaudio-encoder.dll": "fd855e158af393387b3e89a2840c1c8f",
    "enc-amf.dll": "e608e9b0ac3b689ed152e1582aa8c6cc",
    "image-source.dll": "b66e29b66b8fd6cffe6db19ed3076b5b",
    "rtmp-services.dll": "e9f91916d9ede7b0f7ea534186f5d56b",
    "text-freetype2.dll": "a8aa0b6d920470f2191259158996304b",
    "win-capture.dll": "87909a2f3acf369c3e131ad896cca223",
    "win-decklink.dll": "c412934a0f2cf9c1827c4b2e91264df5",
    "win-dshow.dll": "851f9cf3bcd0755161e86103eecda415",
    "win-mf.dll": "117ad112cd53c70738f7287aa57aab3d",
    "win-wasapi.dll": "f57a70a6c70de64de93741dcb3e18968",
    "imgdecoder-gdip.dll": "f666b74be81c5c294777e8fd33ecfd94",
    "render-gdi.dll": "533a317fb6d2e485f76341c4ec807209",
    "ScreenCapture.exe": "59365cefaf409baf3c4de07100684aaf",
    "screen_capture_helper.exe": "90f9898c3ea797e175b56862eb768abc",
    "soui-sys-resource.dll": "6b17e1256ee8d4a6bcd2781c11a38620",
    "soui.dll": "c5cc69e4424241f4bed1ef80b6cf546e",
    "utilities.dll": "870876b906891abd871c99c9b062c72a",
    "libegl.dll": "a333bdd48804314eb82748bbcbc04cbe",
    "libglesv2.dll": "64420ba74b52e8ced1a009adbee04aac",
    "widevinecdm.dll": "f634756cf6a4be877fc71120738ac7f3",
    "KuaiZipShell.dll": "85fdc85ac97988c81be531cd88093841",
    "KuaiZipShellProp.dll": "ff7cd9af1948c1ed41af51c63d9dfff6",
    "KZFormat.dll": "08b0fe1a0bc63c5e6d182aef3f2d255c",
    "KZModule.dll": "aa44c0f986ac24973c12a0822ea8a706",
    "KZMount2.exe": "62e174b2f98b67f1b11d1b49f37e8bb8",
    "Mount.dll": "823cc07c6bef659ea50e2cda5d03d809",
    "MountCore.dll": "b770a7db48d4e1bc784800d79bf5cfcc",
    "Chs_Lang.dll": "6d3acee609f03742b25a9c090779f58f",
    "feedback.exe": "418ffc8e349ad61488e7b137cb5039bc",
    "KuaiZip.exe": "a1ae21f0d7d8634326abfa80f649660f",
    "KuaiZipShell.dll": "d64845da9d930df5f1292ff9afc6e475",
    "KuaiZipShellProp.dll": "96c332b24348ad7f0df0de5d2f885de0",
    "kuaizipUpdateChecker.dll": "dae50ae306dccf02a42e220b2e992263",
    "kuaiZip_dll.dll": "45af291322c84a79f4fda5daff4826dc",
    "KZFormat.dll": "8999fbdc6e17ff0bb1fa2dc0166de46e",
    "KZModule.dll": "0f0dc737bfdc5cfaaf638a46afd01ce4",
    "KZMount2.exe": "60d886d755c41b2ead4e280a7648c6ed",
    "KZReport.exe": "a665a200f778d746443663d2489fcc44",
    "KZReport_dll.dll": "fe0c36028a9c34753748c1a51dc55109",
    "Mount.dll": "8ccd7713b3938e947cb2aaf0e83dd6cc",
    "MountCore.dll": "05bab37f53557a6463752fc6f6c1e854",
    "password.exe": "98a97880fb20b8df06a58b0bca6825bb",
    "repair.exe": "5d08150c0953ed46886c08dcc9d74ef6",
    "service.exe": "18470c6f100d953bbc522fbe443a9c31",
    "skinbox.exe": "1ccf86b43dbe49a715804b9c3ea486dc",
    "uninst.exe": "b0b63c1e59bb965a0f11d14663e1b284",
    "Update.exe": "e96be5faa920d4da52e04645c66a6e91",
    "verify.exe": "822a42add144782bc944cf9ec749199d",
    "vip.exe": "3b23dfbf43285c9d3317e8487d2e1677",
    "wizard.exe": "0142ec7366f3310b40f946b025da5e96",
    "Chs_Lang.dll": "02dee484ae3e3574349da0667a2a9db2",
    "DTLManualUpdate.dll": "4a1cab0184906dfb2ae094e1d4966089",
    "DtlManualUpdate.exe": "19f759b264f3f05fcaac853b6d5fdbf2",
    "DTLNetwork.dll": "ccdab4d0d2d660054b25ab84a493f46b",
    "DtlPlug.dll": "ebff83b17c717ea9175a1dfabdce7723",
    "DTLScreenCapture.exe": "bd864735f937064302512d9d7767b2ec",
    "DTLServHelpProxy.exe": "6249d86fc5e55d7102b791ac950e61b3",
    "DTLServiceHelp.dll": "5939c8abda181f8bf24c6ecdeffd9a85",
    "DTLSoftwarePromoter.dll": "a71ccd224471f3840cea6185f56b8b65",
    "DTLToolbox.dll": "6821d1bcddd489b80442748234ec162f",
    "DTLUI.dll": "ea876f6bf4ec7d6ea1adddd836d5a1c2",
    "DTLWinHelper32.exe": "8eed31d991f334dd5baf399155b501eb",
    "DTLWinHelper64.exe": "53cf796b3daf79204078fb440f79b4d3",
    "DTLzcom.dll": "567a5dca5da5c771129b8fab5dcd746b",
    "FLPCClean.dll": "5ae5276dae637fc4738493759fd53b2d",
    "innoextract.exe": "8892e04b6a3a255b387abd9a659e38c0",
    "pcid.dll": "50faeedba2ecb96e2b471e75666738cf",
    "substat.dll": "68ec336bb85bdd6dd1337830695a6d3f",
    "SystemOpt.dll": "268a21044a1e602f6529e6e2a56413ee",
    "Uninstall.exe": "e17b76afab1e7b0f6c8160e264edda8a",
    "UserCenterCore.exe": "0a382d6d863279d9dad31ba4a7247a30",
    "zlibwapi.dll": "b48fcef13005d61616c50e03528eabef",
    "checkupdate.dll": "6efe5a79d50dda1ce317470414d7d652",
    "dtlupdate.exe": "be059b5b9bbe2411332093df57042b43",
    "PreCheckUpdate.dll": "d751620523b92f98b3d4de76d7cd9826",
    "chrome_elf.dll": "86b3beba2d5e7a3ea4c66513871b2cc8",
    "d3dcompiler_47.dll": "e1677ec0e21e27405e65e31419980348",
    "libcef.dll": "73bd990312622b7cf7a1078663d916db",
    "libEGL.dll": "34b44812b6aad87434d48da3f1a27768",
    "libGLESv2.dll": "6ca750c913f0ced400fb9c09d4d6a77e",
    "vk_swiftshader.dll": "f6058c19e3018432d0ecc906e1c18d09",
    "vulkan-1.dll": "0a6318d36a15556fc0142a9a1a0ddc49",
    "cpuidsdk.dll": "7e375199bc3ade75169397d559451a05",
    "cpuidsdk64.dll": "7bc66d03daf2c17a460b98ce6a64b643",
    "HWInfoSDK.dll": "974abaa05af09cbeb7ef47ef53846ec6",
    "SFTM_LocalSft.dll": "c2da91722104ee26a9f99ac6dee769d6",
    "SoftLocalCheck.dll": "936c7fa0713b3f7a2c3310d57d54b1b5",
    "SoftUninst.dll": "fd8acaff32dd107fa63cbcece2532310",
    "SWBrowser.exe": "b7ad9c365a81dca05c2c2acbfac9d70d",
    "hao123toy.exe": "b2f4567ad1960c4b7d4c6a6bf0943f7d",
    "hao123uninst.exe": "51ac16c0f11835ee7662254830e42f54",
    "SetHomePage.dll": "0de72fd7adde4f3032055a9e454439bc",
    "2345Extract.dll": "df88659d4d2d2dc734cd01c4c7869032",
    "2345SoftMgr.exe": "5cb1e88ae4926b1e7a5cd9a3a91337b2",
    "libcurl_x86.dll": "d2466dd567818a4114f48155304206af",
    "2345Associate.exe": "bd0ee8a50e2d397dae11136240e37602",
    "2345Extract.dll": "e188bcdba947a91d537fd70af2bbdb45",
    "2345MiniUI.dll": "f485068250b3629d26eaf0c6988aebec",
    "2345SafeDispatcher.dll": "86d755ebec05182b385d7af8680f3e29",
    "2345SoftBox.dll": "70191d269d5321d92a7494a5c5347359",
    "2345SoftInstallAgent.exe": "1f6b3805099c26ea7818a5f43d0ec644",
    "2345SoftInstaller.dll": "9db98cce596bddbf7083741d2055aeab",
    "2345SoftInstallHelper.dll": "2023da9dc58e0bb4d4fec8d5e31039f7",
    "2345SoftMgr.exe": "5dbbacb7bacd3eb8a130f4ca4073b56e",
    "2345SoftMgrShell.exe": "8ec247ca83ec7718c0ff535d444f6b5b",
    "2345SoftMgrShell64.exe": "7631a96de2d02a4a5ee4fb7de248e035",
    "2345SoftRI.dll": "038028b5d4602160d8b82cc5127d6a50",
    "2345SoftUninstall.dll": "e6211550f014b9bad781a63f09c7e1db",
    "BasicSQLite.dll": "a6c5e79fd2085565c37ecb10a451ac41",
    "concrt140.dll": "8651e6272e310d5c64d0c91ca975b029",
    "FileAssociate.dll": "e13640eae4324928c0b1d88bd14fd8ba",
    "libcurl_x86.dll": "d2466dd567818a4114f48155304206af",
    "SoftDataCenter.dll": "17b795c90164f8447b31b153edd5e896",
    "SoftMgr.dll": "863ce2063b074a39eb4cd0d015eb9299",
    "SoftMgrMain.dll": "7c569488e8369a96ae1afeebd60e55c2",
    "SoftMgrMenu.dll": "8ddda3ce6c7f75b98fd90dbc2721389f",
    "SoftMgrMenu64.dll": "3dcfd703e355a3c6c4f14df51ee83c80",
    "SoftMgrUI.dll": "d1c07e2f305203c96ccf3ada1f35a8e1",
    "SoftMgrUn.dll": "70f4862e952fdf97bcc2bad3387c358a",
    "SoftNotify.dll": "63b5807b1816f590a4ed076157dd9d1e",
    "ucrtbase.dll": "6343ff7874ba03f78bb0dfe20b45f817",
    "Uninstall.exe": "70aa4d94eee8de60580aa93541c91f5c",
    "vcruntime140.dll": "1b171f9a428c44acf85f89989007c328",
    "ACO.dll": "93d65142a9cafc52c76abe387923c550",
    "AudioPlayer.dll": "d0f87fc45d6a50a961aad203968c49ee",
    "avcodec-58.dll": "bb35fe9c575fba2d6101fef1bc01e83b",
    "avdevice-58.dll": "7fd5f2550e96fa1c891e4051a7b0cd2e",
    "avfilter-7.dll": "a0758c3b5c1bca18d016856f928c73de",
    "avformat-58.dll": "8090c09759ae03e22b2a29c4aa75a906",
    "avutil-56.dll": "c5a5b59552aefb296168fb754eb7d39f",
    "BTBusiness.dll": "d240758192a38d30a3ac6f1dd339ba70",
    "cjson.dll": "78511712d921f4d9c96f49798a46773f",
    "CrashSender1403.exe": "c12437e7fa65277e989d671fe19322d8",
    "D3D10RenderSystem.dll": "1e85147a4d6d315b35121c3bb61b5c18",
    "D3D11RenderSystem.dll": "9762b0a0d2509962fdb19b4780ef8a2b",
    "D3D9RenderSystem.dll": "adc8ef03c971104065fb5702c0402890",
    "D3DCompiler_43.dll": "1c9b45e87528b8bb8cfa884ea0099a85",
    "D3DCompiler_47.dll": "ee5c80b613abf43059ddc29b168bd8d2",
    "d3dx10_43.dll": "20c835843fcec4dedfcd7bffa3b91641",
    "d3dx11_43.dll": "8e0bb968ff41d80e5f2c747c04db79ae",
    "D3DX9_43.dll": "86e39e9161c3d930d93822f1563c280d",
    "dbghelp.dll": "dee832103585ee41bd7f1a905f0726f7",
    "DMCControl.dll": "5ef9bba6d7bf9229093eb0c977436675",
    "DXVA11Decoder.dll": "528b54dfaf1b46d61bde4b515dec1f45",
    "ffprobe.exe": "f0e5a8da429956b770aa7ea0e0f37cc4",
    "FlashPlayer.exe": "82bf0bf007dc94aa6ba8fe3a86f798d6",
    "GLRenderSystem.dll": "3e17ba3f462ff6a5d401fb70f515ee76",
    "HookSheild.dll": "ac16801b474c48bd9b3b89451d3d41ba",
    "imgdecoder-gdip.dll": "b7add63402a5568f81aa121a7e07ba71",
    "imgdecoder-stb.dll": "add518439863f793b693efaac0b8a24b",
    "InterProcessCommunicate.dll": "4a266c9dac9da78aa7bc09b975a41b35",
    "lcurl.dll": "95fafc49cd19c961dc795f1cec3adf3d",
    "libcurl.dll": "ebe6478cace03f1e326cd60c7eba5c53",
    "libeay32.dll": "465e9989e8d18f700195cf3a459a4d58",
    "LocalMediaPlayer.dll": "67d1d1dbaa325362377c8e10b93b0705",
    "LoginPlayer.exe": "bed8272df2e5cfe4fa36e7335297fac2",
    "madVRSetup.exe": "ddb0afe5220bba133f0e99e16008f92a",
    "mb.dll": "0f0869cca2e9cfb9084b95c4ef7d9b78",
    "MediaDecoder.dll": "1ed21512402bd61f29bfc7ec1331f9e2",
    "MediaFileHandler.exe": "309321bb42d3d4b8cba9ea5c2c1bcb49",
    "MediaPlayer.dll": "eec490ded419d23e658984efc98d8340",
    "Miniblink.exe": "0d6bebc963789077baa262be78114307",
    "node.dll": "181d44e74b76a91e8576ff57025dbaa8",
    "postproc-55.dll": "d8054deff36c0bc24c5d0359246335cc",
    "PyPluginManager.dll": "dfa3aae939143c1c7deb41b2e70cdcdd",
    "render-gdi.dll": "065f5161e7641b7ed129055ff86b4c5b",
    "render-skia.dll": "726034c9ae61fd92d4ab75a5c385326b",
    "RenderSystem.dll": "e9810299e937d4733fb9970261de834b",
    "resprovider-zip.dll": "944fd53bf549f513f6770bd4187192a3",
    "riched20.dll": "edb1973e067ee192a8b4200a80e15731",
    "rlottie.dll": "762209eb65a4bcc110b5026d6407f645",
    "RPC.dll": "0752bf0533a908a5527da3e938e57c05",
    "RpcHost.exe": "f7441d2ed42d811c1e1f9181aa826894",
    "RpcMediaDecoder.exe": "2e65b3c5429256bcabaf3ec73de80114",
    "RpcMediaDecoderProxy.dll": "1110ba2ad58540fbab3491bb4a888534",
    "samba.dll": "1e65780e1129bf87e49e121e309984df",
    "scriptmodule-lua.dll": "6b568e77d8276206e84ef1c34dc23a47",
    "ShaderConverter.dll": "340743e18d1f49a90b2573d7036e97ec",
    "soui-sys-resource.dll": "5da924cf22ffdb26115062d6b6630604",
    "soui3.dll": "643959646286263b1802711c35a135ef",
    "SpaceDebrisAdvert.dll": "73f434b06e7f5a833d5ccb51e0395124",
    "ssleay32.dll": "c5de2343c449d94b064334b8fa088026",
    "StellarCmd.exe": "c220c90041c4079f265980f70c0970e0",
    "StellarMediaServer.exe": "6f05afa3ee612e154cfd2e0c7009510e",
    "StellarPlayer.exe": "9d2dc401dc5dfe4c94cb74585f698e93",
    "StellarService.exe": "ec6e46b081562e9c4786a89e376f700e",
    "StellarShellExt.dll": "5aec7ad2199a995e6d661026c653ca05",
    "SubtitleSaver.dll": "78d10dd867606f3de3b58a1a6185167e",
    "swresample-3.dll": "2c4a19b0c826c16727d78fffe6bd7846",
    "swscale-5.dll": "74f6037e265fa9162f959444560ef668",
    "translator.dll": "9e456076ffdae678924f0723dcabbd84",
    "uninst.exe": "1d837a12adf12d4054954f1028c7e505",
    "Updater.exe": "d3a2f80091c7680496ac631fc8636f0b",
    "utilities.dll": "ab8932df740c607f3093e96579471632",
    "zlibwapi.dll": "575f608bd516b04c5616831b9095ee38",
    "lcurl.dll": "95fafc49cd19c961dc795f1cec3adf3d",
    "AudioVisualizerPlugin.dll": "15b9539a18f40ea7fba861bc0f73b58b",
    "BTDemuxer.dll": "24db90de50ef5f2aaa73343f20d7278b",
    "DVDDemuxer.dll": "7339fd136233da65818b2cbd8c9b7793",
    "GifRecorderPlugin.dll": "bf8f2d8927f770f343fa96915d3f8f25",
    "PipeDemuxer.dll": "7a6de0a4585d552136d8be88913fecbc",
    "RawDemuxer.dll": "5ca03969407d0e868a2f990e021eb23d",
    "SambaDemuxer.dll": "ca2ca37c7fad4ee432adc7673ae05ab0",
    "SaveLiveStreamPlugin.dll": "a3d39ad37a2ec0b6c474a12f4d456e8e",
    "SubtitlePlugin.dll": "985fd89d0dd5864ee46a54297a2857ee",
    "UTPDemuxer.dll": "07bd9eb7c8a82fc4d6dcae58407540f7",
    "concrt140.dll": "69f92153570bdf732a15c330c43b6f25",
    "coral_extract.dll": "b1ca8d161f9f34687870dc397bf7fa36",
    "courgette.dll": "79728243d11b42aeeb0a28e32598cc46",
    "icuuc.dll": "c3be84ca844758b401f46b9c5bbd10b1",
    "libcurl_x86.dll": "c1669e0892fe14696cba54ce5f9942a0",
    "node.dll": "0fc1f00467bf6e2c11651e981d7e1a8b",
    "opencv_world451_x86.dll": "35e58ef908fbb021df5d44ef2688445f",
    "pdfium.dll": "f20e9f427a946b08d58a1959585bd5a0",
    "ucrtbase.dll": "df160b9471e9ce9aa4efcfe625673310",
    "Uninstall.exe": "cc2704adf5b63cb67fc5dcb279d5bb0d",
    "vccorlib140.dll": "4e08ee159608c31cbc6c75ec2b4c34f5",
    "vcruntime140.dll": "868239c6e9b109cec1142b20fb45e80c",
    "zlib.dll": "bfa71b1d48905ac43b8d5bd6bac12df0",
    "2345OCRExecutor.exe": "382a4bc507ed864caed1f60cab683389",
    "libiomp5md.dll": "7a26d94b240ac3c9eaa0a4d069cc09d2",
    "mkldnn.dll": "4a0381a4065a43b37d35b64b173a6b80",
    "mklml.dll": "764de114f35e45a90351a2d1bdde820d",
    "opencv_world451.dll": "5e816f3f737bd1effdff8710df5fb080",
    "paddle_inference.dll": "b1c00aea10b72e0f050f289a7fb8ab85",
    "vcomp140.dll": "e29d050b82ec6129211dc8821f56a202",
    "AuthorityProtectUI.dll": "b6e902e8cd7dbf72b713a8288c2267f5",
    "AvScan.dll": "1a105d9fca0ba5d5d5f63004439a7d49",
    "AvShellExt.dll": "7251e7c67a14dc7f69b3b3c5a135f041",
    "AvShellExt64.dll": "92e46d2ad815d6d74f5caf060bdd69ff",
    "AvShellExtUwpApp.dll": "c9ac2de942595fd66b801832565092cb",
    "BasicBusiness.dll": "10b38e674ce0db0f398b426f9d8df43d",
    "BasicBusiness.dll": "792d5486d0d3a7a4d9f60959ee92e022",
    "BasicBusinessConfigCenter.dll": "6b7aaa4974500edaeea0fdbe1b939d89",
    "BasicSQLite.dll": "8ce5c951b3ce57b48b78d90a1e9525c1",
    "concrt140.dll": "8651e6272e310d5c64d0c91ca975b029",
    "courgette_dll.dll": "8696e7407f9f2691a399de78887f02cc",
    "DriverApi.dll": "be14709693dc180b9bd575726ffc98f9",
    "DriverInstall.dll": "56698a04033c325241b815aee2a35d91",
    "libcurl_x86.dll": "26bfaba6e2ec66be566c2649b3a6cafd",
    "LicXPlugin.dll": "7d3e0396c7af8735fde7c571e0242ccd",
    "lua53.dll": "1469517920b25f8cb21a0898bb7ecb09",
    "NsProtectApi.dll": "436d581334d99a879448b00e58ce57b4",
    "ProtectApi.dll": "554d321b579a65ae9870f73a1c15dd12",
    "ProtectApi64.dll": "387193a6024be63188e4f293fe3e955f",
    "ProtectLogistics.dll": "0d8f4eb01afe049a2695d71bd20ef5ef",
    "SafeCenterUpdate.dll": "d71f6e441fe63135f3fae58da7a5b1dc",
    "SafeExpMon.dll": "83af06d04c9c6eec47d9f0351ffe86fa",
    "SafeExpMon64.dll": "6f7a745a2752e925de21b91734f1db5f",
    "SafeWebMon.dll": "9104cc31bf15eac1f26ea9dcfd2401f2",
    "SafeWebMon64.dll": "0c7b775241579594f66064c586142c7b",
    "SdAntiVBusCore.dll": "11ade6397160bce5568049cae6d22bac",
    "SdAntiVCache.dll": "8be814235ab14cda4f3b6fb848663645",
    "SdAntiVCloud.dll": "5611242d567d3c9af38da6458f1537e9",
    "SdAntiVEngine.dll": "f8d92042b5d4821fe8bd41d89cbd4f45",
    "SdAviraSndPlugin.dll": "44a90e94886709dc6350217ac47a15f7",
    "SdConfigCenter.dll": "1e0351ef5d48d3c09dc4c41838c03ac0",
    "SdDefenceLogic.dll": "8a39cf4a3bd02d81d9acb3840a4e3600",
    "SdEsswSndPlugin.dll": "aa2edab83036469889eb51a22aaebea4",
    "SdFileAssociate.dll": "723d39dab1e0448f93f380077354d61e",
    "SdGDOperate.dll": "237fb8878119113fe1ad390e63fa07db",
    "SdHipsDefProtect.dll": "a5515b1c4a8e524720c94f94506a10c4",
    "SdHipsLogic.dll": "43fd8f2eb4f119259f75876345649be6",
    "SdHipsUpdate.dll": "85bdf8231015b3be8baddeecb4c11c01",
    "SdHipsWebProtect.dll": "536364f551f2476d39d8572289ff67d5",
    "SdInstallProtect.dll": "7096c5fd172d2be0a937534f83e9f797",
    "SdMsgProtect.dll": "f32c7997310efd5e542a738a08862ea2",
    "SdProtectManagerUI.dll": "88261a3962725c825b63166edc744a01",
    "SdReflectDefender.dll": "054d8c589321ef24ef63bd19dbcb3d8c",
    "SdRTPLog.dll": "ecca3d59d8ba9a2e0cb4a7b31196a594",
    "SdRtProtect.dll": "7f360b2ce25358e8c698a15797c192ba",
    "SdRTProtectUI.dll": "4be7b8b43015195e39faddc77f724667",
    "SdRTProtectUICtrl.dll": "033a7ea8dbe904ddfb10754cd4e2f0fd",
    "SdTrojaneEngine.dll": "ba19576ea17880ee15c461f45064a1e3",
    "SdUIList.dll": "e21f7fc49088b939efb53e2995f334c6",
    "TkNitrome.dll": "f9b527c0a285bdb9f53e76e85b27ca3f",
    "TkNitrome64.dll": "1376ff268e2a998eefd92018da3e32b6",
    "ucrtbase.dll": "6343ff7874ba03f78bb0dfe20b45f817",
    "Uninstall.exe": "1139e5ac24c3304633726d7e1d580d4d",
    "vcruntime140.dll": "1b171f9a428c44acf85f89989007c328",
    "WebProtect.dll": "3c44d14f8910c9c707095530ce351d9a",
    "2345DirectUI.dll": "a598e5300dfbd17892743bfbbb23ea38",
    "2345Uninst.exe": "f3eb9a969d6294b40977e8992bb1fb28",
    "concrt140.dll": "abdef5f24d965beb17acc7948b4bebfd",
    "coral_extract.dll": "118f2884a77ed527a39d98c466d2cec4",
    "DuiLib.dll": "9fac2a1d04d622fa08235e34a7e9637d",
    "ImageCompress.dll": "a8677a28a4dd5f1aef286a5360d01077",
    "ImageCompressCore.dll": "fac243a2736730b1c45f2be52c0f3cf2",
    "ImageCvt.dll": "0ee5f4e5b9723c0e78724658bea7d8d8",
    "ImageMagickPlus.dll": "91baed39b8d46afb4aa8acc9cf3feafc",
    "PicCompressTask.exe": "ad3ab146d2a974cda7edf9f90ddcbabe",
    "PicCompressTaskApp.dll": "e8b9c8e4f7dec4398930c24a96319c5d",
    "2345Cad.exe": "92d2e606fff3a67f7ebcaba9d1b89ba6",
    "2345CadApp.dll": "f9a42fac29fd5472013511cc1f7335bb",
    "2345CadSDK.dll": "1ac3a35f4d16c8c8869d86e2bfa81f3b",
    "concrt140.dll": "8fc1c2f2ebb7e46df30ecd772622b0bc",
    "ucrtbase.dll": "ed82e9c6c4f7a475d7fd6ebabf3fab2a",
    "vccorlib140.dll": "164561905f701bc680d654232bb5c4d1",
    "vcruntime140.dll": "943fc74c2e39fe803d828ccfa7e62409",
    "vcruntime140_1.dll": "05052be2c36166ff9646d7d00bb7413f",
    "vcruntime140_threads.dll": "997c522f929b39d93b1d179bc94b0486",
    "2345ImageRes_x125.dll": "fc3579215dc353ecbd31162a6a6a858f",
    "2345ImageRes_x150.dll": "2bcbf8b8460d5c11fb645a09cdb0f439",
    "2345Pdf_x100.dll": "5a8e9b383affa5d81bfdd74ef37a783d",
    "2345Pdf_x125.dll": "09dc7abf3d2498cc96020738c772496a",
    "2345Pdf_x200.dll": "c2b74013321b6971dd6bf3590a2b56d0",
    "2345ImageLang_chs.dll": "288cb8b24d164e6ec75709b024b943cf",
    "2345PicApi.dll": "a6241692d9998102d44806c911e26e5f",
    "ComPDFKit.Desk.dll": "daec8c225f87b7b4fffbfabe5ab06eb5",
    "ComPDFKit.Viewer.dll": "bcee5199060ca89dcade9d4abde877b0",
    "Dragablz.dll": "28f4947fda81ed3e419ed92f216c070a",
    "icuuc.dll": "c3be84ca844758b401f46b9c5bbd10b1",
    "libcurl.dll": "c172489d9014c4fa3f395898018a764c",
    "libcurl_x86.dll": "286944bc17f13962057397146d6aa1d4",
    "libeay32.dll": "05e59901acca4a1ea3bb2934e3b4a6bc",
    "log4net.dll": "70f9f728511a7d372d0e71aaf17a741f",
    "Newtonsoft.Json.dll": "0ed248f9cf0b97fb2f7a307f498d9169",
    "PdfEditor.exe": "1f34d86c33c11318f1ed68b608582d43",
    "pdfium.dll": "f20e9f427a946b08d58a1959585bd5a0",
    "PDFiumApi.dll": "a2a8e584c74badb5d9abb6aa624660de",
    "RCFLApi.dll": "f045e8486a3e405e6e7e5eb9fe2160a9",
    "ssleay32.dll": "4d1702fde267098693cf3a0047812e7e",
    "UpdateTimeDate.exe": "1b8c6b8b9a9b1cb63280cdd78de3fbc4",
    "vcruntime140.dll": "1b171f9a428c44acf85f89989007c328",
    "WpfAnimatedGif.dll": "a5f3052e7a24cd94b815fce5c8d65c94",
    "WpfMiniBlink.dll": "2d5bf8071ef23b4a322b3c1e4012ef1c",
    "zlib.dll": "bfa71b1d48905ac43b8d5bd6bac12df0",
    "zlibwapi.dll": "2a5fd7a70a0be2e458135501ae14f716",
    "ngen.exe": "417d6ea61c097f8df6fef2a57f9692df",
    "ucrtbase_clr0400.dll": "bfe20e1d9bebe61cd8898663fdacb74e",
    "vcruntime140_clr0400.dll": "071309be821483287a0fe982aef005c1",
    "WpfApp.exe": "5db861404131be50bcdf5def168dcd6f",
    "ngen.exe": "b6c3fe33b436e5006514403824f17c66",
    "ucrtbase_clr0400.dll": "f8f171be1820544e15b555847005355c",
    "vcruntime140_clr0400.dll": "63936588122bdee9624d02ce3f8f54ea",
    "WpfApp.exe": "a0df7d41660446f00ac33a39991f27ee",
    "ComPDFKit.dll": "0790f6ad6eb447d7ba52bf788d218154",
    "AssistPic.exe": "336d7379a7802a8304bad1f6c8cc1a18",
    "AssistPicMain.dll": "bc993b43ad8699cc5c68b4627d4484fa",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "PicService.dll": "1ec3fe29f044977c234c9f740929a518",
    "PicService.exe": "8448c7d8b500d0d1d2d789a7f09187a8",
    "PicServiceManager.exe": "0a699ec44fd157d2b44b7f61daf70497",
    "Tool_Uninstall.exe": "92fa415319da6bef3de5b316c89726c1",
    "AssistPic.exe": "4e75595f9cba2f97eb6671aff5968d6f",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "PicService.dll": "b257a44c31df52f33d8816147cffc07d",
    "2345ImageThumbCore64.dll": "17678d0550636b72d89a2163a64b95b4",
    "FreeImage.dll": "e32f21bae72fe91d8ccddb0b955ac21d",
    "FreeImagePlus.dll": "c4d94cbf3ebb223347cc773e78ffe475",
    "2345PicMgr.dll": "f9b527c0a285bdb9f53e76e85b27ca3f",
    "2345PicMgr64.dll": "1376ff268e2a998eefd92018da3e32b6",
    "2345Capture.exe": "8e983dfa4acd05d7fa9da731d5547470",
    "2345CaptureApp.dll": "175a4b0ab4ff4c4cfe1a8c68c1358614",
    "2345DirectUI.dll": "23558ee019f5a337ab57a5196af3a732",
    "2345PinyinCloud.exe": "cf7a6454f9a98499bd9ff57b63f5ddb3",
    "2345PinyinConfig.exe": "e1ca7dee7143deb3612084220b18b702",
    "2345PinyinCourgette.dll": "52a6004ac85171e326f8fe90e5e4c32a",
    "2345PinyinExtract.dll": "3fc0a88814bf0ff9c686f2613c870cf5",
    "2345PinyinInstall.exe": "19b6af75a1adb9852655b94b68b4cd27",
    "2345PinyinInstall64.exe": "19b6af75a1adb9852655b94b68b4cd27",
    "2345PinyinSkinUtil.exe": "0117dff2400bf578cf97e21c20598186",
    "2345PinyinSymbol.exe": "88a131d23754c8221cf4ea33c3442f7b",
    "2345PinyinTool.exe": "3b61d59b7601ccff346c3e1b158d286f",
    "2345PinyinUpdate.exe": "d4796274c1d2ac45bae1e849ffad0533",
    "2345PinyinWizard.exe": "64bba42b1ee45d9527fd06c0252d7bad",
    "FaceTool_2345Pinyin.exe": "2d981d42c1ede144dc7feb78f0a510e8",
    "libcurl_x86.dll": "651e411d7f1bae7a8cf453d6bdf5e120",
    "Uninstall.exe": "dfee5a091ea5eb1262258265ee6224a3",
    "AssistPinyin.exe": "5824e89f2b231b9dabdbd276ebaba792",
    "AssistPinyinMain.dll": "69e83a0b30a6188b6edf3488053f4fa6",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "courgette_dll.dll": "3a7533f3e1f50bb1be29d103e57ea6c6",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "PinyinService.dll": "f8fbca0eb7be921afb05029e7460bc00",
    "PinyinService.exe": "963f37559bdd5f116adcc00b53498476",
    "PinyinServiceManager.exe": "e118f23760986695b64834a98c781aea",
    "Tool_Uninstall.exe": "d68d24f1101a6ce2614826fa1da8f637",
    "AssistPinyin.exe": "60ff3c13c957c59ab5fd41fee97578ce",
    "coral_extract.dll": "38b4c50710126bb520741eb8f0e89657",
    "libcurl_x86.dll": "fe4400f13cbfae5eabefe7a1f33a1c9c",
    "PinyinService.dll": "f8399cca724574b503a77b9d86d4a4d0",
    "2345PinyinMgr.dll": "f9b527c0a285bdb9f53e76e85b27ca3f",
    "2345PinyinMgr64.dll": "1376ff268e2a998eefd92018da3e32b6",
    "2345Associate.exe": "02e4f563b8d57b618d8596727cab86e7",
    "2345Extract.dll": "a8867b4da3da21b02e6e7c3af7a3c1c5",
    "2345HipsSet.exe": "800bbabd63f2dbc78c87cb3f8d1a6570",
    "2345InstDLL.dll": "857b4c211f1f11cd7660d52b6a36d992",
    "2345InstDll.exe": "3ba6eb17e9f07c438d9a4a03af9cf665",
    "2345MiniUI.dll": "4e81d951db274ef2dcd0e8d8b52b5fa2",
    "2345ProtectManager.exe": "76b22de7742fd3c32b910c7b2f0d3486",
    "2345RTProtect.exe": "e4fea1d423e70d4f6b9807d5b4622a71",
    "2345SafeBho.dll": "f36cae9bd04bb34691db3c19ca74e4d4",
    "2345SafeBho64.dll": "b12ef0a13dd9f5883ec28b89300e27df",
    "2345SafeCenterCrashReport.exe": "c8e8fdf0193802acb83a3efc07a81e4d",
    "2345SafeCenterInstaller.exe": "4daa9ed9699550a85dff1795d5edcd1c",
    "2345SafeCenterSvc.exe": "8bbc9928aa2e6bcc3fbcbc1a445fa0d7",
    "2345SafeCenterUpdate.exe": "9dc2a85de123373852a68677bbe98303",
    "2345ScUpgrade.exe": "1babf87d52edd429d579bc1919281515",
    "2345SFGuard.exe": "0b691ee7fc23b6b2f7814b5d9720ac7b",
    "2345SFGuard64.exe": "bbb3d81b809c50663ca07fac0c66adef",
    "2345SFWebShell.exe": "c99896e928b0ae446b57c8054a16c703",
    "2345VirusScan.exe": "78a42558bdb1261b2195d9613a1af7d8",
    "BasicBusinessConfigCenter.dll": "7103aa49a3cd7608e43aebb5d2d4a1fa",
    "BasicSQLite.dll": "d9e301905b6cee26164c96d80d002dd2",
    "concrt140.dll": "8651e6272e310d5c64d0c91ca975b029",
    "courgette_dll.dll": "8696e7407f9f2691a399de78887f02cc",
    "Exam.dll": "98fbeae8b1ef082443edc9545a9f211d",
    "FileShre.dll": "ffb3cf311da1116670fbb8473e1dcb67",
    "FileShreUI.dll": "f29462e3b5eecf3a5bc186636147064d",
    "FuncAssistant.dll": "ab7efc45ebf85c3df3b047ea38bf36fc",
    "LeakFix.dll": "2b8a3359c940466244b5fb6734e4623e",
    "LeakFixEngine.dll": "56e6f206fc624954b2867ea22e4a6346",
    "LeakFixUI.dll": "550e7b3597bd486bff17f0d66a6b3808",
    "libcurl_x86.dll": "84de60b3970f4f3c0e0c05d73e15391a",
    "LSPFix.dll": "7bcfdfe842ce7658aa7493cf35464dcb",
    "LSPFixUI.dll": "bc60d0ca6f5c98dc5cb3078397170696",
    "lua53.dll": "9dcfa722be30c9002199ff5c8a51221e",
    "LuaBizBasic.dll": "6b88d145060f646c9aab5f7249bee5a2",
    "ManuUpdate.dll": "9f7f824c1227be12095a04cf7ed55770",
    "NetFlow.dll": "fc9a204a28dad9bf9804059bb0396f00",
    "NetFlowUI.dll": "56f682304ea1bfb4f3fdfe1c5dbce4be",
    "NetRepair.dll": "8f764217d5c11d6cd416c971c5981dd4",
    "NetRepairUI.dll": "d438d6b178e918c5daf4f62d5128b396",
    "Optimize.dll": "38b072cb2f0a46c5424ad77b1eb027df",
    "RMenuMgr.exe": "586dac65e7d92883b59af717e2137023",
    "RtProtectCenterUI.dll": "36840acee75c486622397c754bf3916e",
    "SafeLockUI.dll": "af2b0db8a135b0f04e3deba07ccb19c0",
    "SafeTray.dll": "80d605be37b3c05d66a182225a4809f5",
    "SafeTrayUI.dll": "40634847634509fa8240e576f6603c75",
    "SafeUI.dll": "8a7df8f520ce91ad16b1d6961b1b9b5b",
    "SafeUpdate.dll": "3c3dd93e0218ec0c1d90c632630e1025",
    "SafeUpdateUI.dll": "4ebd9adccd16002b293e840157dddd71",
    "SdAntiVBusCore.dll": "d06b90270cd4b20ea8c749ba3fcb02b3",
    "SettingUI.dll": "83e76d1b914ab4f2d01af0dd0e6b69bb",
    "SysDoctor.dll": "a1db051adc2e7c837a382fefcc4f8a10",
    "SysDoctorUI.dll": "205e05d7d02936d70688bf1a71fc9ff7",
    "Trash.dll": "8e4274b00d0c8a5893e51a0e5773476f",
    "TrashRcmdUI.dll": "e25a561a3b1965adac2e2b16fe46e00a",
    "ucrtbase.dll": "6343ff7874ba03f78bb0dfe20b45f817",
    "Uninstall.exe": "e68fb216b386997952004dbfe9298eed",
    "UsbGuard.dll": "499e271a71ff64a6380349523559a84c",
    "UsbGuardUI.dll": "60df58455c03b99a61c72bf8422af98f",
    "vcruntime140.dll": "1b171f9a428c44acf85f89989007c328",
    "2345Extract.dll": "a8867b4da3da21b02e6e7c3af7a3c1c5",
    "2345SafeCenterInstaller.exe": "4daa9ed9699550a85dff1795d5edcd1c",
    "libcurl_x86.dll": "26bfaba6e2ec66be566c2649b3a6cafd",
    "2345Extract.dll": "e188bcdba947a91d537fd70af2bbdb45",
    "2345SoftMgr.exe": "5dbbacb7bacd3eb8a130f4ca4073b56e",
    "2345Excel2Pdf.dll": "ea93736e2c56124d3584b485738a6538",
    "2345ImageSDK.dll": "bd19bbe847db8c66e47ed7db629d52cb",
    "2345PdfAsposeSDK.dll": "6dc8693b65f61cdaaa79b9c923a05ac5",
    "2345PdfConverter.dll": "d50e374b2467f9759927b6791dd5ddf3",
    "2345PdfDumper.exe": "e7ce6800beaa3d07d3c381500460b1de",
    "2345PdfFeedback.exe": "f887e207fceba03a0207f9c20dcbdf51",
    "2345PdfHelper.exe": "b4c633b16957283196c967dba31a12de",
    "2345PdfInfo.dll": "b3406c9bab1e20b625651d3bf60290a2",
    "2345PdfLoader.exe": "821947d3e85d24e1f94b4063350c652d",
    "2345PdfMain.exe": "1b977efafc990fa96f0fa10b5a54fbac",
    "2345PdfProcess.exe": "808e50722ab2b8299cba0c5aef705369",
    "2345PdfTaskApp.dll": "d7a1f2fd99040ccdd35a2b67157bc4a6",
    "2345PdfTool.exe": "a2edd45de34d403cf513813996bb50fa",
    "2345PdfUpdate.exe": "65771f2b394be98d351e54dd9e8af332",
    "2345PdfWorker.exe": "d4dbff19ab9078aa862a249d5f424516",
    "2345PPT2Pdf.dll": "8a3b676ec7aae519279077117c7d30c9",
    "2345Preview.dll": "f8a9f6f93f602f2a1df08c66e5add2e5",
    "2345PreviewWorker.exe": "c20d0339181d2f56c03f4c87d9bc2132",
    "2345Uninst.exe": "f9010c8ea3ef7b23c867361d1b1a727c",
    "2345Word2Pdf.dll": "0c4926187de096e8f50956cfae01851d",
}


def is_virus_file(file_path):
    fname = os.path.basename(file_path)

    if fname in VIRUS_NAMES:
        return True

    for kw in KEYWORDS:
        if kw.lower() in fname.lower():
            return True

    try:
        with open(file_path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        if md5 in VIRUS_MD5.values():
            return True
    except Exception:
        pass
    return False

def calc_md5(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def kill_processes(adware_files):
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            name = proc.info['name']
            if name and name.lower() in adware_files:
                proc.kill()
        except Exception:
            continue

def remove_startup_items(adware_files):
    run_keys = [
        (winreg.HKEY_CURRENT_USER, r'Software\\Microsoft\\Windows\\CurrentVersion\\Run'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Run'),
    ]
    for root, path in run_keys:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                to_delete = []
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        for adware in adware_files:
                            if adware[:-4] in value.lower():
                                to_delete.append(name)
                        i += 1
                    except OSError:
                        break
                for name in to_delete:
                    winreg.DeleteValue(key, name)
        except Exception:
            continue

    startup_folders = [
        os.path.join(os.environ['APPDATA'], r'Microsoft\\Windows\\Start Menu\\Programs\\Startup'),
        os.path.join(os.environ['PROGRAMDATA'], r'Microsoft\\Windows\\Start Menu\\Programs\\Startup'),
    ]
    for folder in startup_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                for adware in adware_files:
                    if file.lower().startswith(adware[:-4]):
                        try:
                            os.remove(os.path.join(folder, file))
                        except Exception:
                            pass

def remove_context_menu():
    shell_paths = [
        r'*\\shell',
        r'Directory\\shell',
        r'AllFileSystemObjects\\shell',
        r'Folder\\shell',
    ]
    for root in [winreg.HKEY_CLASSES_ROOT]:
        for path in shell_paths:
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                    i = 0
                    to_delete = []
                    while True:
                        try:
                            subkey = winreg.EnumKey(key, i)
                            for kw in KEYWORDS:
                                if kw in subkey:
                                    to_delete.append(subkey)
                            i += 1
                        except OSError:
                            break
                    for subkey in to_delete:
                        try:
                            winreg.DeleteKey(key, subkey)
                        except Exception:
                            pass
            except Exception:
                continue

def remove_2345pinyin_ime():
    ime_root = r'SYSTEM\\CurrentControlSet\\Control\\Keyboard Layouts'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ime_root, 0, winreg.KEY_ALL_ACCESS) as key:
            i = 0
            to_delete = []
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey) as sk:
                        try:
                            desc, _ = winreg.QueryValueEx(sk, 'Layout Text')
                            if '2345' in desc:
                                to_delete.append(subkey)
                        except Exception:
                            pass
                    i += 1
                except OSError:
                    break
            for subkey in to_delete:
                try:
                    winreg.DeleteKey(key, subkey)
                except Exception:
                    pass
    except Exception:
        pass

def remove_uninstall_entries():
    uninstall_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
    ]
    for root, path in uninstall_keys:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                to_delete = []
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey) as sk:
                            try:
                                disp, _ = winreg.QueryValueEx(sk, 'DisplayName')
                                for kw in KEYWORDS:
                                    if kw in disp:
                                        to_delete.append(subkey)
                            except Exception:
                                pass
                        i += 1
                    except OSError:
                        break
                for subkey in to_delete:
                    try:
                        winreg.DeleteKey(key, subkey)
                    except Exception:
                        pass
        except Exception:
            continue

def remove_group_policy():
    policy_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\\Policies'),
        (winreg.HKEY_CURRENT_USER, r'SOFTWARE\\Policies'),
    ]
    for root, path in policy_paths:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                to_delete = []
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        for kw in KEYWORDS:
                            if kw in subkey:
                                to_delete.append(subkey)
                        i += 1
                    except OSError:
                        break
                for subkey in to_delete:
                    try:
                        winreg.DeleteKey(key, subkey)
                    except Exception:
                        pass
        except Exception:
            continue

def remove_related_registry():
    reg_roots = [
        (winreg.HKEY_CURRENT_USER, r'SOFTWARE'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE'),
    ]
    for root, path in reg_roots:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                to_delete = []
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        for kw in KEYWORDS:
                            if kw in subkey:
                                to_delete.append(subkey)
                        i += 1
                    except OSError:
                        break
                for subkey in to_delete:
                    try:
                        winreg.DeleteKey(key, subkey)
                    except Exception:
                        pass
        except Exception:
            continue

def search_and_delete_virus():
    for root, dirs, files in os.walk(C_DRIVE):
        if root.lower().startswith(WINDOWS_DIR.lower()):
            continue
        for file in files:
            full_path = os.path.join(root, file)
            if is_virus_file(full_path):
                try:
                    os.remove(full_path)
                    print(f"已删除病毒文件: {full_path}")
                except Exception:
                    pass
    remove_target_folders()

def remove_target_folders():
    target_folders = [
        '2345Downloads', '2345Explorer', '2345Soft', '2345游戏大厅', 'BirdWallpaper', 'DesktopLite', 'DTLSoft',
        'Hao123Desk', 'SoftMgr_2345', 'StellarPlayer', 'TSBrowser', '快压', '360DesktopLite', '360Game5',
        '360huabao', '360Reader', '360se6'
    ]
    search_dirs = [os.environ['USERPROFILE'], 'C:\\']
    for base_dir in search_dirs:
        for root, dirs, files in os.walk(base_dir):
            for folder in target_folders:
                if folder in dirs:
                    folder_path = os.path.join(root, folder)
                    try:
                        shutil.rmtree(folder_path)
                        print(f"已删除文件夹: {folder_path}")
                    except Exception:
                        pass
def restore_browser_shortcuts():
    for file in os.listdir(DESKTOP):
        if file.lower().endswith('.lnk'):
            for browser in BROWSER_NAMES:
                if browser.lower() in file.lower():
                    shortcut_path = os.path.join(DESKTOP, file)
                    try:
                        import pythoncom
                        from win32com.shell import shell, shellcon
                        shortcut = pythoncom.CoCreateInstance(
                            shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
                        persist_file.Load(shortcut_path)
                        shortcut.SetArguments("")
                        persist_file.Save(shortcut_path, 0)
                    except Exception:
                        pass

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\\Microsoft\\Internet Explorer\\Main', 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, 'Start Page', 0, winreg.REG_SZ, 'about:blank')
    except Exception:
        pass

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\\Microsoft\\Edge\\Main', 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, 'Start Page', 0, winreg.REG_SZ, 'about:blank')
    except Exception:
        pass

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\\Google\\Chrome\\PreferenceMACs', 0, winreg.KEY_ALL_ACCESS) as key:
            pass  
    except Exception:
        pass

    try:
        import json
        import glob
        user_dir = os.path.expandvars(r'%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default')
        pref_path = os.path.join(user_dir, 'Preferences')
        if os.path.exists(pref_path):
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            if 'session' in prefs and 'startup_urls' in prefs['session']:
                prefs['session']['startup_urls'] = ['about:blank']
            if 'homepage' in prefs:
                prefs['homepage'] = 'about:blank'
            if 'homepage_is_newtabpage' in prefs:
                prefs['homepage_is_newtabpage'] = False
            with open(pref_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    try:
        import configparser
        ff_profiles = glob.glob(os.path.expandvars(r'%APPDATA%\\Mozilla\\Firefox\\Profiles\\*'))
        for profile in ff_profiles:
            prefs_path = os.path.join(profile, 'prefs.js')
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(prefs_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip().startswith('user_pref("browser.startup.homepage"'):
                            f.write('user_pref("browser.startup.homepage", "about:blank");\n')
                        else:
                            f.write(line)
    except Exception:
        pass

    try:
        chromium_dir = os.path.expandvars(r'%LOCALAPPDATA%\\Chromium\\User Data\\Default')
        pref_path = os.path.join(chromium_dir, 'Preferences')
        if os.path.exists(pref_path):
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            if 'session' in prefs and 'startup_urls' in prefs['session']:
                prefs['session']['startup_urls'] = ['about:blank']
            if 'homepage' in prefs:
                prefs['homepage'] = 'about:blank'
            if 'homepage_is_newtabpage' in prefs:
                prefs['homepage_is_newtabpage'] = False
            with open(pref_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    try:
        opera_dir = os.path.expandvars(r'%APPDATA%\\Opera Software\\Opera Stable')
        pref_path = os.path.join(opera_dir, 'Preferences')
        if os.path.exists(pref_path):
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            if 'session' in prefs and 'startup_urls' in prefs['session']:
                prefs['session']['startup_urls'] = ['about:blank']
            if 'homepage' in prefs:
                prefs['homepage'] = 'about:blank'
            if 'homepage_is_newtabpage' in prefs:
                prefs['homepage_is_newtabpage'] = False
            with open(pref_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if __name__ == "__main__":
    main_gui()
    print("查杀完成！请重启电脑。")
