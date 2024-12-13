"""add triggers

Revision ID: 1b2e91014b4e
Revises: c4c4ea41ac02
Create Date: 2024-12-13 18:19:48.485835

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b2e91014b4e"
down_revision: str | None = "c4c4ea41ac02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION public.update_timestamp()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.update_updated_at()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        NEW.updated_at = current_timestamp;
        RETURN NEW;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.membership_payments_audit_trigger()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO public.membership_payments_audit(payment_id, operation, operation_timestamp, old_data) VALUES (OLD.payment_id, 'DELETE', now(), row_to_json(OLD));
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO public.membership_payments_audit(payment_id, operation, operation_timestamp, old_data, new_data) VALUES (NEW.payment_id, 'UPDATE', now(), row_to_json(OLD), row_to_json(NEW));
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO public.membership_payments_audit(payment_id, operation, operation_timestamp, new_data) VALUES (NEW.payment_id, 'INSERT', now(), row_to_json(NEW));
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.addresses_audit_trigger()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO public.addresses_audit(address_id, operation, operation_timestamp, old_data) VALUES (OLD.address_id, 'DELETE', now(), row_to_json(OLD));
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO public.addresses_audit(address_id, operation, operation_timestamp, old_data, new_data) VALUES (NEW.address_id, 'UPDATE', now(), row_to_json(OLD), row_to_json(NEW));
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO public.addresses_audit(address_id, operation, operation_timestamp, new_data) VALUES (NEW.address_id, 'INSERT', now(), row_to_json(NEW));
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.emails_audit_trigger()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO public.emails_audit(email_id, operation, operation_timestamp, old_data) VALUES (OLD.email_id, 'DELETE', now(), row_to_json(OLD));
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO public.emails_audit(email_id, operation, operation_timestamp, old_data, new_data) VALUES (NEW.email_id, 'UPDATE', now(), row_to_json(OLD), row_to_json(NEW));
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO public.emails_audit(email_id, operation, operation_timestamp, new_data) VALUES (NEW.email_id, 'INSERT', now(), row_to_json(NEW));
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.phones_audit_trigger()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO public.phones_audit(phone_id, operation, operation_timestamp, old_data) VALUES (OLD.phone_id, 'DELETE', now(), row_to_json(OLD));
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO public.phones_audit(phone_id, operation, operation_timestamp, old_data, new_data) VALUES (NEW.phone_id, 'UPDATE', now(), row_to_json(OLD), row_to_json(NEW));
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO public.phones_audit(phone_id, operation, operation_timestamp, new_data) VALUES (NEW.phone_id, 'INSERT', now(), row_to_json(NEW));
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $function$
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION public.registration_audit_trigger()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO public.registration_audit(registration_id, operation, operation_timestamp, old_data) VALUES (OLD.registration_id, 'DELETE', now(), row_to_json(OLD));
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO public.registration_audit(registration_id, operation, operation_timestamp, old_data, new_data) VALUES (NEW.registration_id, 'UPDATE', now(), row_to_json(OLD), row_to_json(NEW));
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO public.registration_audit(registration_id, operation, operation_timestamp, new_data) VALUES (NEW.registration_id, 'INSERT', now(), row_to_json(NEW));
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    $function$
    """)

    # Create triggers
    op.execute("""
    CREATE TRIGGER phones_audit_trigger_after
    AFTER INSERT OR DELETE OR UPDATE ON public.phones
    FOR EACH ROW EXECUTE FUNCTION public.phones_audit_trigger();
    """)

    op.execute("""
    CREATE TRIGGER update_timestamp_before_update_phones
    BEFORE UPDATE ON public.phones
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    """)

    op.execute("""
    CREATE TRIGGER update_updated_at_trigger
    BEFORE UPDATE ON public.registration
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
    """)

    op.execute("""
    CREATE TRIGGER registration_audit_trigger_after
    AFTER INSERT OR DELETE OR UPDATE ON public.registration
    FOR EACH ROW EXECUTE FUNCTION public.registration_audit_trigger();
    """)

    op.execute("""
    CREATE TRIGGER emails_audit_trigger_after
    AFTER INSERT OR DELETE OR UPDATE ON public.emails
    FOR EACH ROW EXECUTE FUNCTION public.emails_audit_trigger();
    """)

    op.execute("""
    CREATE TRIGGER update_timestamp_before_update_emails
    BEFORE UPDATE ON public.emails
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    """)

    op.execute("""
    CREATE TRIGGER addresses_audit_trigger_after
    AFTER INSERT OR DELETE OR UPDATE ON public.addresses
    FOR EACH ROW EXECUTE FUNCTION public.addresses_audit_trigger();
    """)

    op.execute("""
    CREATE TRIGGER update_timestamp_before_update_addresses
    BEFORE UPDATE ON public.addresses
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    """)

    op.execute("""
    CREATE TRIGGER membership_payments_audit_trigger_after
    AFTER INSERT OR DELETE OR UPDATE ON public.membership_payments
    FOR EACH ROW EXECUTE FUNCTION public.membership_payments_audit_trigger();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS phones_audit_trigger_after ON public.phones;")
    op.execute("DROP TRIGGER IF EXISTS update_timestamp_before_update_phones ON public.phones;")
    op.execute("DROP TRIGGER IF EXISTS update_updated_at_trigger ON public.registration;")
    op.execute("DROP TRIGGER IF EXISTS registration_audit_trigger_after ON public.registration;")
    op.execute("DROP TRIGGER IF EXISTS emails_audit_trigger_after ON public.emails;")
    op.execute("DROP TRIGGER IF EXISTS update_timestamp_before_update_emails ON public.emails;")
    op.execute("DROP TRIGGER IF EXISTS addresses_audit_trigger_after ON public.addresses;")
    op.execute(
        "DROP TRIGGER IF EXISTS update_timestamp_before_update_addresses ON public.addresses;"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS membership_payments_audit_trigger_after ON public.membership_payments;"
    )

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS public.update_timestamp();")
    op.execute("DROP FUNCTION IF EXISTS public.update_updated_at();")
    op.execute("DROP FUNCTION IF EXISTS public.membership_payments_audit_trigger();")
    op.execute("DROP FUNCTION IF EXISTS public.addresses_audit_trigger();")
    op.execute("DROP FUNCTION IF EXISTS public.emails_audit_trigger();")
    op.execute("DROP FUNCTION IF EXISTS public.phones_audit_trigger();")
    op.execute("DROP FUNCTION IF EXISTS public.registration_audit_trigger();")
