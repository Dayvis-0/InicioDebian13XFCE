#!/usr/bin/env python3
"""
Debian 13 XFCE - Boot & Login Configuration Manager
Gestor modular para personalizar y respaldar GRUB, Plymouth y LightDM.
"""

import os
import sys
import shutil
import platform
import subprocess
from datetime import datetime
from pathlib import Path


class BootConfigManager:
    def __init__(self):
        self.script_dir = Path(__file__).resolve().parent
        self.assets_dir = self.script_dir / "assets"
        self.backup_dir = self.script_dir / "backups"
        
        # Rutas del sistema
        self.grub_default = Path("/etc/default/grub")
        self.grub_debian_theme = Path("/etc/grub.d/05_debian_theme")
        self.grub_linux_script = Path("/etc/grub.d/10_linux")
        self.grub_themes_dir = Path("/boot/grub/themes")
        
        self.plymouth_themes_dir = Path("/usr/share/plymouth/themes")
        
        self.lightdm_conf = Path("/etc/lightdm/lightdm-gtk-greeter.conf")
        self.gtk_themes_dir = Path("/usr/share/themes")

    def check_privileges(self):
        """Verifica que el script se ejecute con privilegios de root"""
        if os.geteuid() != 0:
            print("\n❌ Este script requiere permisos de superusuario (sudo).")
            print("👉 Ejecutalo con: sudo python3 boot_config_manager.py\n")
            return False
        return True

    def detect_environment(self):
        """Valida que sea un sistema Linux compatible (Debian)"""
        if platform.system() != "Linux":
            print("❌ Este script solo funciona en Linux.")
            return False
            
        print("✅ Sistema operativo: Linux")
        
        # Verificar utilidades necesarias
        missing = []
        for cmd in ["update-grub", "plymouth-set-default-theme"]:
            if not shutil.which(cmd) and not Path(f"/usr/sbin/{cmd}").exists():
                missing.append(cmd)
                
        if missing:
            print(f"⚠️ Advertencia: No se encontraron los siguientes comandos en PATH: {', '.join(missing)}")
        return True

    def create_backup(self):
        """Crea un respaldo completo de las configuraciones actuales antes de modificar"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_backup = self.backup_dir / f"backup_{timestamp}"
        dest_backup.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📦 Creando respaldo del sistema en: {dest_backup}")
        
        # 1. Backup GRUB
        if self.grub_default.exists():
            shutil.copy2(self.grub_default, dest_backup / "grub")
        if self.grub_debian_theme.exists():
            shutil.copy2(self.grub_debian_theme, dest_backup / "05_debian_theme")
        if self.grub_linux_script.exists():
            shutil.copy2(self.grub_linux_script, dest_backup / "10_linux")
            
        # 2. Backup LightDM
        if self.lightdm_conf.exists():
            shutil.copy2(self.lightdm_conf, dest_backup / "lightdm-gtk-greeter.conf")
            
        print("✅ Respaldo completado exitosamente.")
        return dest_backup

    def configure_grub(self):
        """Configura el tema Astronaut en GRUB y optimiza parámetros del kernel"""
        print("\n🚀 [1/3] Configurando GRUB...")
        
        # 1. Copiar assets del tema
        target_theme = self.grub_themes_dir / "astronaut"
        target_theme.mkdir(parents=True, exist_ok=True)
        src_theme = self.assets_dir / "grub"
        
        if src_theme.exists():
            for item in src_theme.iterdir():
                dest = target_theme / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            print("   ✅ Assets de GRUB copiados a /boot/grub/themes/astronaut")
        else:
            print("   ⚠️ No se encontraron assets de GRUB en la carpeta local.")

        # 2. Modificar /etc/default/grub
        if self.grub_default.exists():
            content = self.grub_default.read_text(encoding="utf-8")
            
            # Parámetros óptimos del kernel
            cmdline = 'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3 udev.log_level=3 vt.global_cursor_default=0 i915.fastboot=1"'
            theme_line = 'GRUB_THEME="/boot/grub/themes/astronaut/theme.txt"'
            bg_line = 'GRUB_BACKGROUND="/boot/grub/themes/astronaut/background.png"'
            
            lines = content.splitlines()
            new_lines = []
            has_theme = False
            has_bg = False
            
            for line in lines:
                if line.startswith("GRUB_CMDLINE_LINUX_DEFAULT="):
                    new_lines.append(cmdline)
                elif line.startswith("GRUB_THEME="):
                    new_lines.append(theme_line)
                    has_theme = True
                elif line.startswith("GRUB_BACKGROUND="):
                    new_lines.append(bg_line)
                    has_bg = True
                else:
                    new_lines.append(line)
                    
            if not has_theme:
                new_lines.append(theme_line)
            if not has_bg:
                new_lines.append(bg_line)
                
            self.grub_default.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print("   ✅ /etc/default/grub configurado con tema y arranque silencioso")

        # 3. Ocultar mensajes de carga intermedia
        if self.grub_linux_script.exists():
            txt = self.grub_linux_script.read_text(encoding="utf-8")
            if 'quiet_boot="0"' in txt:
                txt = txt.replace('quiet_boot="0"', 'quiet_boot="1"')
                self.grub_linux_script.write_text(txt, encoding="utf-8")
                print("   ✅ Mensajes de carga de kernel silenciados en GRUB")

        # 4. Actualizar GRUB
        print("   ⏳ Ejecutando update-grub...")
        subprocess.run(["update-grub"], check=True)
        print("✅ GRUB actualizado correctamente.")

    def configure_plymouth(self):
        """Configura el tema de pantalla de carga Plymouth (astronaut-wind)"""
        print("\n🌌 [2/3] Configurando Plymouth Boot Splash...")
        
        target_plymouth = self.plymouth_themes_dir / "astronaut-wind"
        target_plymouth.mkdir(parents=True, exist_ok=True)
        src_plymouth = self.assets_dir / "plymouth"
        
        if src_plymouth.exists():
            for item in src_plymouth.iterdir():
                dest = target_plymouth / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            print("   ✅ Assets de Plymouth copiados a /usr/share/plymouth/themes/astronaut-wind")
        
        # Aplicar y reconstruir initramfs
        print("   ⏳ Reconstruyendo initramfs (esto puede tardar unos segundos)...")
        cmd = "/usr/sbin/plymouth-set-default-theme" if Path("/usr/sbin/plymouth-set-default-theme").exists() else "plymouth-set-default-theme"
        subprocess.run([cmd, "-R", "astronaut-wind"], check=True)
        print("✅ Plymouth configurado y reconstruido en initramfs.")

    def configure_lightdm(self):
        """Configura la pantalla de inicio de sesión LightDM y el tema GTK Astronaut-Grub"""
        print("\n🔑 [3/3] Configurando Login (LightDM)...")
        
        # 1. Instalar tema GTK
        target_gtk = self.gtk_themes_dir / "Astronaut-Grub" / "gtk-3.0"
        target_gtk.mkdir(parents=True, exist_ok=True)
        src_css = self.assets_dir / "lightdm" / "gtk.css"
        
        if src_css.exists():
            shutil.copy2(src_css, target_gtk / "gtk.css")
            print("   ✅ Tema GTK Astronaut-Grub instalado en /usr/share/themes/")
            
        # 2. Configurar /etc/lightdm/lightdm-gtk-greeter.conf
        src_conf = self.assets_dir / "lightdm" / "lightdm-gtk-greeter.conf"
        if src_conf.exists():
            shutil.copy2(src_conf, self.lightdm_conf)
            print("   ✅ /etc/lightdm/lightdm-gtk-greeter.conf actualizado")
            
        # Limpiar posibles archivos conflictivos en .d
        conf_d = Path("/etc/lightdm/lightdm-gtk-greeter.conf.d/01_astronaut.conf")
        if conf_d.exists():
            conf_d.unlink()
            
        print("✅ LightDM configurado correctamente.")

    def apply_all(self):
        """Ejecuta la configuración completa de todos los módulos"""
        self.create_backup()
        self.configure_grub()
        self.configure_plymouth()
        self.configure_lightdm()
        print("\n🎉 ¡TODAS LAS CONFIGURACIONES FUERON APLICADAS CON ÉXITO!")
        print("💡 Podés reiniciar el equipo para apreciar el arranque completo.")

    def restore_backup(self):
        """Permite restaurar un respaldo previo"""
        backups = sorted(list(self.backup_dir.glob("backup_*")))
        if not backups:
            print("\n❌ No hay respaldos disponibles para restaurar.")
            return
            
        print("\n📂 Respaldos disponibles:")
        for idx, b in enumerate(backups, 1):
            print(f"  [{idx}] {b.name}")
            
        try:
            choice = int(input("\n👉 Selecciona el número de respaldo a restaurar (0 para cancelar): "))
            if choice == 0 or choice > len(backups):
                print("Cancelado.")
                return
                
            selected = backups[choice - 1]
            print(f"\nRestaurando desde: {selected.name}...")
            
            if (selected / "grub").exists():
                shutil.copy2(selected / "grub", self.grub_default)
            if (selected / "05_debian_theme").exists():
                shutil.copy2(selected / "05_debian_theme", self.grub_debian_theme)
            if (selected / "10_linux").exists():
                shutil.copy2(selected / "10_linux", self.grub_linux_script)
            if (selected / "lightdm-gtk-greeter.conf").exists():
                shutil.copy2(selected / "lightdm-gtk-greeter.conf", self.lightdm_conf)
                
            subprocess.run(["update-grub"], check=True)
            print("✅ Respaldo restaurado y GRUB actualizado.")
        except ValueError:
            print("Opción no válida.")

    def menu(self):
        """Menú interactivo de opciones"""
        while True:
            print("\n" + "=" * 55)
            print("   🌌 DEBIAN 13 XFCE - BOOT & LOGIN MANAGER 🌌")
            print("=" * 55)
            print("  1) 🚀 Aplicar TODO (GRUB + Plymouth + LightDM)")
            print("  2) 📦 Configurar solo GRUB (Astronaut Theme)")
            print("  3) 🌌 Configurar solo Plymouth (Splash Screen)")
            print("  4) 🔑 Configurar solo Login (LightDM GTK Theme)")
            print("  5) 💾 Crear Respaldo manual ahora")
            print("  6) ⏪ Restaurar un Respaldo anterior")
            print("  0) ❌ Salir")
            print("=" * 55)
            
            try:
                opc = input("👉 Elige una opción: ").strip()
                if opc == "1":
                    self.apply_all()
                elif opc == "2":
                    self.create_backup()
                    self.configure_grub()
                elif opc == "3":
                    self.create_backup()
                    self.configure_plymouth()
                elif opc == "4":
                    self.create_backup()
                    self.configure_lightdm()
                elif opc == "5":
                    self.create_backup()
                elif opc == "6":
                    self.restore_backup()
                elif opc == "0":
                    print("\n¡Hasta luego!")
                    break
                else:
                    print("\n⚠️ Opción no válida.")
            except KeyboardInterrupt:
                print("\nOperación cancelada por el usuario.")
                break


def main():
    manager = BootConfigManager()
    if not manager.check_privileges():
        sys.exit(1)
    if not manager.detect_environment():
        sys.exit(1)
        
    # Soporte para argumento directo '--all'
    if len(sys.argv) > 1 and sys.argv[1] in ["--all", "-a", "all"]:
        manager.apply_all()
    else:
        manager.menu()


if __name__ == "__main__":
    main()
