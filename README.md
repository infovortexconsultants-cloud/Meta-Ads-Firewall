Vortex - Meta Ads Firewall

This branch adds a packaged layout, main entrypoint, installer script, and a systemd unit.

Build
  ./packaging/build.sh

Install (run as root)
  ./packaging/install.sh

Run and debug
  systemctl status meta-ads-firewall
  journalctl -u meta-ads-firewall -f

Configuration
  /etc/meta-ads-firewall/config.yaml (installer copies example here)
