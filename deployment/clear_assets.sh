#!/bin/bash
# Clear Odoo asset bundles cache and restart
sudo -u postgres psql odoo_2026_01_27 << 'SQLEOF'
DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';
SQLEOF
echo "Cache efface. Redemarrage..."
sudo systemctl restart odoo
sleep 2
sudo systemctl status odoo --no-pager | grep -E "Active|Started"
echo "Termine!"
