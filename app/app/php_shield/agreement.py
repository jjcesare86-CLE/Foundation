"""
PHP Shield -- Site Owner Authorization and Consent Agreement.

*** DRAFT -- ATTORNEY REVIEW REQUIRED BEFORE USE WITH REAL CUSTOMERS. ***
This text was written by an AI assistant, not a lawyer. It has not been reviewed for
enforceability in any jurisdiction. Counsel must supply: the contracting legal entity,
governing law/venue, and confirm the liability limits, before launch. See DECISIONS.md.

The text a signer sees is rendered server-side from this template (the client never
supplies agreement text). The SHA-256 of the exact rendered text is stored with the
signature, together with the text itself, so exactly what was signed can always be shown.
"""
import hashlib

AGREEMENT_VERSION = "2026-10-v1-DRAFT"

_TEMPLATE = """SITE OWNER AUTHORIZATION AND CONSENT AGREEMENT
Version {version}

DRAFT - ATTORNEY REVIEW REQUIRED

Order: {order_id}
Website (the "Site"): {domain}
Service purchased: {scope}

This agreement is between you (the "Site Owner") and PHP Shield, a service of Automaition Nation ("PHP Shield", "we", "us"). By signing below you give us permission to work on the Site as described here. Please read it carefully.

1. You own or control the Site.
You confirm that you own the Site and its domain, or that you are legally authorized by the owner to give the permissions in this agreement. If you are not sure, do not sign.

2. What you authorize us to do.
For the Site named above, and only for the service you purchased, you authorize PHP Shield to:
  (a) scan the Site, using only publicly visible signals and ordinary web requests;
  (b) access the Site and its hosting account using the access details you give us through the secure hand-off we provide;
  (c) back up the Site's files and database;
  (d) modify the Site, including upgrading PHP and updating or patching WordPress core, plugins, themes, libraries and custom code, as needed to deliver the service; and
  (e) run further scans before and after the work, and, if you bought the Maintenance Plan, monthly scans afterwards.

3. Scope.
Our work is limited to the service tier you purchased ({scope}). Work outside that scope needs your separate written agreement. We will not access or change any website, domain or system other than the Site.

4. Backups and rollback.
Before changing anything we will take a backup and keep a way to restore the Site. You understand that updating software can change how a site looks or behaves, and that some older plugins, themes or custom code may stop working on a newer PHP version. If something breaks we will try to restore the backup. You agree to keep your own independent backups as well.

5. No guarantee.
We work to reduce the Site's exposure to known vulnerabilities, but we cannot guarantee the Site will never be hacked, will be free of vulnerabilities, or will keep working with every plugin or integration. New vulnerabilities are discovered all the time; being fixed today does not make the Site safe from future ones.

6. Limitation of liability.
To the fullest extent the law allows, PHP Shield's total liability for anything connected to this agreement or the service is limited to the amount you paid us for the order above, and we are not liable for indirect or consequential losses such as lost profits, lost sales or loss of data that a backup could have restored. Nothing in this agreement limits liability that cannot legally be limited.

7. Your responsibilities.
You will give us accurate information, will share access details only through the secure hand-off (never by ordinary email, chat or the intake form), will tell us about anything on the Site that must not be changed, and will keep your hosting account, domain and payment details in good standing.

8. Third parties.
Your hosting provider, plugin and theme authors, and other third parties are outside our control. If your hosting agreement restricts who may access or change the Site, you are responsible for making sure our work is permitted.

9. Confidentiality and data.
We will keep the Site's access details and contents confidential, use them only to deliver the service, and delete access details when the work is finished and no Maintenance Plan is active.

10. Revoking permission.
You may revoke this authorization at any time by using the revoke option on your order page or emailing us. After we receive it we will stop accessing the Site and will not start new work; revocation does not by itself entitle you to a refund for work already done, and it ends any Maintenance Plan scans. Revoking does not undo changes already made.

11. Electronic signature.
You agree that typing your name below and ticking the confirmation box is your legal signature, equal to a handwritten one. We record the time, your IP address and browser details, and a fingerprint of this exact text, as evidence of what you agreed to.

12. Governing law.
[Governing law and venue to be completed by counsel before launch.]
"""


def render(*, domain: str, order_id: str, scope: str) -> str:
    """Deterministic per order: the same inputs always give the same text and hash, so the
    text a customer reads (GET) is byte-identical to what is hashed when they sign (POST).
    The signing time is recorded separately, never inside the hashed text."""
    return _TEMPLATE.format(version=AGREEMENT_VERSION, order_id=order_id, domain=domain, scope=scope)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
