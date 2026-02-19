# Sale vs Cash Report Module for Odoo

## Overview
The **Sale vs Cash Report** module generates a detailed report of sales and cash transactions for selected customers (partners) within a specified date range.  
It also includes the **salesperson** assigned to each partner for better tracking and accountability.

This module is designed for **Odoo 18** but can be adapted to earlier versions with minor adjustments.

---

## Features
- Generate a report of total sales, total cash received, and balance per customer.
- Include **opening balance** before the report start date.
- Filter by multiple customers.
- Filter by date range (`date_from` and `date_to`).
- Display the **salesperson** assigned to each customer.
- Automatically calculates the final balance:


---

## Models
### Wizard: `ask_sale_vs_cash_report`
Used to select:
- Customers (`partner_ids`)
- Date range (`date_from`, `date_to`)

### Report: `sale_vs_cash_template`
Generates the report using SQL queries on:
- `account_move_line` (journal entries)
- `account_move` (invoices & refunds)
- `res_partner` (customers)
- `res_users` (salesperson)

---

## Installation
1. Place the module in your custom addons folder, e.g.:
2. Update the app list in Odoo.
3. Install the **Sale vs Cash Report** module.
4. Access the report via:

---

## Usage
1. Open the **Sale vs Cash Report** wizard.
2. Select one or more customers.
3. Set the **From Date** and **To Date**.
4. Click **Generate Report**.
5. The report will display:
- Customer Name
- Salesperson Name
- Opening Balance
- Total Sale
- Total Cash
- Final Balance

---

## Example Output
| Partner Name | Salesperson | Opening Balance | Total Sale | Total Cash | Balance |
|--------------|------------|----------------|-----------|------------|---------|
| ABC Ltd      | John Doe   | 5000           | 15000     | 10000      | 10000   |
| XYZ Inc      | Jane Smith | 2000           | 8000      | 5000       | 5000    |

---

## Notes
- The module relies on `posted` account moves only.
- Only **receivable accounts** (`account_type = 'asset_receivable'`) are considered.
- If no partners are selected, the report returns an empty result set.

---

## Author
**Roshaan Ahmad**  
Email: roshaan@asksol.pk
Company: **Asksol**
Date: 2026-02-19

---

## License
This module is released under the **AGPL-3 license** and is free to use and modify.
