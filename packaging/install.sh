#!/usr/bin/env bash
set -euo pipefail

APPNAME=meta-ads-firewall
INSTALL_DIR=/opt/${APPNAME}
BIN_PATH=${INSTALL_DIR}/${APPNAME}
SERVICE_FILE=/etc/systemd/system/${APPNAME}.service
CONFIG_DIR=/etc/${APPNAME}

if [ "$EUID" -ne 0 ]; then
  echo 'Please run as root'
  exit 1
fi

echo 'Vortex - Meta Ads Firewall Installer'

# Create system user if missing
if ! id -u metaadsfw >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin metaadsfw
fi

mkdir -p "${INSTALL_DIR}"
chown metaadsfw:metaadsfw "${INSTALL_DIR}"

if [ ! -f ./dist/${APPNAME} ]; then
  echo "Executable ./dist/${APPNAME} not found. Build it first with packaging/build.sh"
  exit 2
fi

cp ./dist/${APPNAME} "${BIN_PATH}"
chmod 0755 "${BIN_PATH}"
chown metaadsfw:metaadsfw "${BIN_PATH}"

cp packaging/${APPNAME}.service "${SERVICE_FILE}"
chmod 0644 "${SERVICE_FILE}"

mkdir -p "${CONFIG_DIR}"
if [ ! -f "${CONFIG_DIR}/config.yaml" ]; then
  cp config/config.example.yaml "${CONFIG_DIR}/config.yaml"
  chmod 0640 "${CONFIG_DIR}/config.yaml"
  chown root:metaadsfw "${CONFIG_DIR}/config.yaml"
fi

mkdir -p /var/lib/${APPNAME}
chown metaadsfw:metaadsfw /var/lib/${APPNAME}

systemctl daemon-reload
systemctl enable --now ${APPNAME}.service

echo 'Installed ${APPNAME}. Edit /etc/${APPNAME}/config.yaml and then: systemctl restart ${APPNAME}.service'
