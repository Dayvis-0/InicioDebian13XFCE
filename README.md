# 🌌 InicioDebian13XFCE - Boot & Login Manager

Gestor automatizado para personalizar y respaldar la experiencia visual completa de inicio en **Debian 13 XFCE**:

1. **GRUB 2:** Tema visual *Astronaut*, alta resolución y arranque silencioso sin parpadeos (*flicker-free*).
2. **Plymouth (Boot Splash):** Pantalla de carga limpia con el fondo del astronauta y texto *"Iniciando Debian..."* en fuente `Roboto Bold 38`.
3. **LightDM (Login):** Pantalla de inicio de sesión estilizada con el tema GTK `Astronaut-Grub` (paleta Catppuccin Mocha, caja posicionada a la derecha y barra superior estilizada).

---

## 📁 Estructura del Proyecto

```text
InicioDebian13XFCE/
├── assets/
│   ├── grub/             # Imágenes y fuentes del tema Astronaut de GRUB
│   ├── plymouth/         # Scripts y wallpapers de la pantalla de carga
│   └── lightdm/          # Tema GTK (gtk.css) y configuración del greeter
├── backups/              # Respaldos automáticos creados antes de modificar el sistema
├── boot_config_manager.py # Gestor principal en Python (interactivo y CLI)
└── README.md             # Documentación
```

---

## 🚀 Uso del Gestor

Navegá al directorio e iniciá el script con permisos de superusuario:

```bash
cd ~/Documentos/Estudio/Carrera/Configuraciones/InicioDebian13XFCE
sudo python3 boot_config_manager.py
```

### Menú Interactivo:
- **1) Aplicar TODO:** Realiza un respaldo automático y aplica GRUB, Plymouth y LightDM de una sola vez.
- **2) Configurar solo GRUB:** Aplica el tema *Astronaut* y parámetros de kernel.
- **3) Configurar solo Plymouth:** Aplica el boot splash *astronaut-wind* y actualiza `initramfs`.
- **4) Configurar solo Login:** Aplica el tema GTK *Astronaut-Grub* en LightDM.
- **5) Crear Respaldo manual:** Guarda una copia de seguridad con fecha y hora.
- **6) Restaurar Respaldo:** Permite regresar a cualquier estado guardado previamente.

### Modo Automático (CLI):
```bash
sudo python3 boot_config_manager.py --all
```
