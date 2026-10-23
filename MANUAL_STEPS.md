# MANUAL_STEPS — only what you must do by hand, in order

PowerShell. Everything else is done and tested. Foundation PR is **#5**, site PR is **automaition-nation #2**.
Start in `C:\dev\Foundation`.

## 1. Create PHP Shield's Supabase project and load the database
1. https://supabase.com/dashboard -> **New project** -> name `php-shield`, pick a region, set a database password -> **Create new project**.
2. Copy all three migrations to your clipboard (they sort into the right order):
   ```powershell
   Get-Content C:\dev\Foundation\supabase-php-shield\migrations\*.sql | Set-Clipboard
   ```
3. Supabase -> **SQL Editor** -> **New query** -> paste (Ctrl+V) -> **Run**. Expect "Success. No rows returned".
4. Supabase -> **Project Settings -> API**. Copy **Project URL** (= `PHP_SHIELD_SUPABASE_URL`) and the **service_role** key (= `PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY`).

## 2. Stripe (test mode first): products, prices and webhook in one command
1. Stripe Dashboard, **Test mode** on -> **Developers -> API keys** -> copy the **Secret key** (`sk_test_...`).
2. Run (it prints every value you need in step 4):
   ```powershell
   cd C:\dev\Foundation
   pip install stripe pyyaml
   $env:STRIPE_SECRET_KEY = "sk_test_PASTE_HERE"
   python scripts\create_stripe_products.py --webhook-url https://php-shield-api.onrender.com/php-shield/stripe/webhook
   ```
   Keep the output: `STRIPE_PRICE_PHPSHIELD_BASIC / _STANDARD / _COMPLEX / _MAINTENANCE` and `STRIPE_WEBHOOK_SECRET`.

## 3. Merge the Foundation PR
```powershell
gh pr ready 5 --repo jjcesare86-CLE/Foundation
gh pr merge 5 --repo jjcesare86-CLE/Foundation --squash
```

## 4. Deploy on Render
1. https://dashboard.render.com -> **New -> Blueprint** -> connect repo `jjcesare86-CLE/Foundation`, branch `main`.
2. Set **Blueprint file path** to `render.php-shield.yaml` -> **Apply**. It creates `php-shield-api` and `php-shield-monthly-rescan`.
3. Paste the values it asks for (same values on both services where both ask):

   | Variable | Value |
   |---|---|
   | `PHP_SHIELD_SUPABASE_URL` | Project URL from step 1 |
   | `PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY` | service_role key from step 1 |
   | `STRIPE_SECRET_KEY` | `sk_test_...` from step 2 |
   | `STRIPE_WEBHOOK_SECRET` | `whsec_...` printed in step 2 |
   | `STRIPE_PRICE_PHPSHIELD_BASIC` / `_STANDARD` / `_COMPLEX` / `_MAINTENANCE` | the four `price_...` ids printed in step 2 |
   | `RESEND_API_KEY` | the same key `an-sales-pipeline` already uses (Render -> an-sales-pipeline -> Environment) |
   | `PHP_SHIELD_OWNER_EMAIL` | the mailbox that should get order/authorization/alert emails |

4. Wait for `php-shield-api` to show **Live**. If its URL is **not** `https://php-shield-api.onrender.com`, also: (a) in Stripe -> Developers -> Webhooks edit the endpoint URL to `<your URL>/php-shield/stripe/webhook`, and (b) in Render -> `automaition-nation` -> Environment set `VITE_PHP_SHIELD_API_URL` to `<your URL>`.

## 5. Verify the deployment
```powershell
cd C:\dev\Foundation
python scripts\php_shield_verify_deploy.py https://php-shield-api.onrender.com
```
Every line must say PASS. A FAIL line names the missing variable.

## 6. Publish the site pages
```powershell
gh pr ready 2 --repo jjcesare86-CLE/automaition-nation
gh pr merge 2 --repo jjcesare86-CLE/automaition-nation --squash
```
Render redeploys `automaition-nation` automatically. Then open https://automaitionnation.com/php-shield.

## 7. One real end-to-end test (test mode)
1. On `/php-shield`, scan a site **you own**, open the report, buy any tier with card `4242 4242 4242 4242` (any future date, any CVC).
2. Complete intake, sign, and verify ownership (add the TXT record or upload the file shown). Check you got the owner emails and the customer got the signed PDF.
3. Admin page: https://php-shield-api.onrender.com/php-shield/admin — key is Render -> `php-shield-api` -> Environment -> `PHP_SHIELD_ADMIN_API_KEY` (Reveal). Start work, tick the checklist, Deliver.

## 8. Legal (blocks real customers)
Send `app\app\php_shield\agreement.py` (the text between the triple quotes) to your attorney. They must supply the legal entity name and governing law. When approved, edit that file and change `AGREEMENT_VERSION` to remove `-DRAFT`.

## 9. Go live (only after 7 and 8)
```powershell
cd C:\dev\Foundation
$env:STRIPE_SECRET_KEY = "sk_live_PASTE_HERE"
python scripts\create_stripe_products.py --live --webhook-url https://php-shield-api.onrender.com/php-shield/stripe/webhook
```
In Render -> `php-shield-api` -> Environment replace `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` and the four `STRIPE_PRICE_PHPSHIELD_*` with the new printed values -> **Save, rebuild, and deploy**. Re-run step 5, then make one small real purchase and refund it in Stripe.
