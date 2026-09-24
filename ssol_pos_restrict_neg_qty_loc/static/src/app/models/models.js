/** @odoo-module */

import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PosStore.prototype, {

    async pay() {
        const order = this.getOrder();
        const lines = order.getOrderlines();

        let call_super = true;

        if (this.env.services.pos.config.restrict_zero_qty) {

            // POS ki source location
            const locationId =
                this.env.services.pos.config.picking_type_id
                    .default_location_src_id.id;

            /*
             * Order mein jo products hain unki IDs
             */
            const productIds = [
                ...new Set(
                    lines
                        .filter(line => line.qty > 0)
                        .map(line => line.product_id.id)
                )
            ];

            /*
             * Backend se fresh stock.quant data
             */
            let freshQuants = [];

            if (productIds.length > 0) {
                freshQuants = await this.data.orm.searchRead(
                    "stock.quant",
                    [
                        ["product_id", "in", productIds],
                        ["location_id", "=", locationId],
                    ],
                    [
                        "id",
                        "product_id",
                        "lot_id",
                        "location_id",
                        "quantity",
                    ]
                );
            }

            /*
             * Har order line ka stock check
             */
            for (const line of lines) {

                if (line.qty <= 0) {
                    continue;
                }

                const product = line.product_id;

                // Sirf consumable products
                if (product.type !== "consu") {
                    continue;
                }

                /*
                 * Agar lot selected hai
                 */
                const lotName =
                    line.pack_lot_ids?.[0]?.lot_name || null;

                /*
                 * Product + Location + Lot wise stock
                 */
                let stockQuants;

                if (lotName) {

                    stockQuants = freshQuants.filter((quant) =>
                        quant.product_id?.[0] === product.id &&
                        quant.location_id?.[0] === locationId &&
                        quant.lot_id?.[1] === lotName
                    );

                } else {

                    stockQuants = freshQuants.filter((quant) =>
                        quant.product_id?.[0] === product.id &&
                        quant.location_id?.[0] === locationId &&
                        !quant.lot_id
                    );
                }

                /*
                 * Total available quantity
                 */
                const totalQty = stockQuants.reduce(
                    (sum, quant) => sum + (quant.quantity || 0),
                    0
                );

                console.log(
                    "Product:",
                    product.display_name,
                    "Location:",
                    locationId,
                    "Lot:",
                    lotName,
                    "Available:",
                    totalQty,
                    "Requested:",
                    line.qty
                );

                /*
                 * Stock available nahi
                 */
                if (stockQuants.length === 0 || totalQty <= 0) {

                    call_super = false;

                    const lotDisplay = lotName
                        ? ` [${lotName}]`
                        : "";

                    this.dialog.add(AlertDialog, {
                        title: _t("Zero Quantity Not Allowed"),
                        body: _t(
                            `${product.display_name}${lotDisplay} is out of stock.`
                        ),
                    });

                    break;
                }

                /*
                 * Requested quantity > available quantity
                 */
                if (line.qty > totalQty) {

                    call_super = false;

                    const lotDisplay = lotName
                        ? ` [${lotName}]`
                        : "";

                    this.dialog.add(AlertDialog, {
                        title: _t("Deny Order"),
                        body: _t(
                            `${product.display_name}${lotDisplay} has only ${totalQty} quantity available.`
                        ),
                    });

                    break;
                }
            }
        }

        /*
         * Agar stock available hai to normal payment
         */
        if (call_super) {
            await super.pay();
        }
    },
});

