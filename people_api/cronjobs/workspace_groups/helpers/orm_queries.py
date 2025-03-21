"""This module contains functions to get emails from the database."""

import logging

from sqlmodel import and_, col, func, select, text

from people_api.database.models import (
    Emails,
    LegalRepresentatives,
    MembershipPayments,
    Registration,
)
from people_api.dbs import get_async_sessions


async def get_active_adult_emails() -> list[tuple[str, str]]:
    """Get emails of active adult members"""
    logging.log(logging.INFO, "Getting active adult emails from database")
    all_results: list[tuple[str, str]] = []
    async for sessions in get_async_sessions():
        # Build subquery for active adults based on payments and age
        active_adults = (
            select(col(Registration.registration_id))
            .distinct()
            .join(
                MembershipPayments,
                col(Registration.registration_id) == col(MembershipPayments.registration_id),
            )
            .where(
                and_(
                    col(Registration.expelled).is_(False),
                    col(Registration.deceased).is_(False),
                    col(MembershipPayments.expiration_date) >= func.current_date(),
                    col(Registration.birth_date)
                    <= func.current_date() - text("interval '18 years'"),
                )
            )
            .subquery()
        )

        # Get emails from emails table
        emails_union = select(
            col(Emails.registration_id), col(Emails.email_address).label("email")
        ).subquery()

        # Final query joining active adults with their emails
        result = (
            await sessions.ro.exec(
                select(active_adults.c.registration_id, emails_union.c.email)
                .distinct()
                .join(
                    emails_union,
                    active_adults.c.registration_id == emails_union.c.registration_id,
                )
                .where(emails_union.c.email.is_not(None))
            )
        ).all()

        all_results.extend(result)

    return all_results


async def get_inactive_adult_emails() -> list[tuple[str, str]]:
    """Get emails of inactive adult members"""
    logging.log(logging.INFO, "Getting inactive adult emails from database")
    all_results: list[tuple[str, str]] = []
    async for sessions in get_async_sessions():
        # Build subquery for getting max expiration date per registration
        max_expiration = (
            select(
                col(MembershipPayments.registration_id),
                func.max(col(MembershipPayments.expiration_date)).label("max_date"),
            )
            .group_by(col(MembershipPayments.registration_id))
            .subquery()
        )

        # Build subquery for inactive adults based on payments and age
        inactive_adults = (
            select(col(Registration.registration_id))
            .distinct()
            .outerjoin(
                max_expiration,
                col(Registration.registration_id) == col(max_expiration.c.registration_id),
            )
            .where(
                and_(
                    col(Registration.expelled).is_(False),
                    col(Registration.deceased).is_(False),
                    func.coalesce(max_expiration.c.max_date, text("'1900-01-01'"))
                    < func.current_date(),
                    col(Registration.birth_date)
                    <= func.current_date() - text("interval '18 years'"),
                )
            )
            .subquery()
        )

        # Get emails from emails table
        emails_union = select(
            col(Emails.registration_id), col(Emails.email_address).label("email")
        ).subquery()

        # Final query joining inactive adults with their emails
        result = (
            await sessions.ro.exec(
                select(inactive_adults.c.registration_id, emails_union.c.email)
                .distinct()
                .join(
                    emails_union,
                    inactive_adults.c.registration_id == emails_union.c.registration_id,
                )
                .where(emails_union.c.email.is_not(None))
            )
        ).all()

        all_results.extend(result)

    return all_results


async def get_active_jb_emails() -> list[tuple[str, str]]:
    """Get emails of active junior branch members"""
    logging.log(logging.INFO, "Getting active JB emails from database")
    all_results: list[tuple[str, str]] = []
    async for sessions in get_async_sessions():
        # Build subquery for active JBs based on payments and age
        active_jbs = (
            select(col(Registration.registration_id))
            .distinct()
            .join(MembershipPayments)
            .where(
                and_(
                    col(Registration.expelled).is_(False),
                    col(Registration.deceased).is_(False),
                    col(MembershipPayments.expiration_date) >= func.current_date(),
                    col(Registration.birth_date)
                    > func.current_date() - text("interval '18 years'"),
                )
            )
            .subquery()
        )

        # Combine emails from both registration emails and legal representatives
        emails_union = (
            select(col(Emails.registration_id), col(Emails.email_address).label("email"))
            .union(
                select(
                    col(LegalRepresentatives.registration_id),
                    col(LegalRepresentatives.email).label("email"),
                )
            )
            .subquery()
        )

        # Final query joining active JBs with their emails
        result = (
            await sessions.ro.exec(
                select(emails_union.c.registration_id, emails_union.c.email)
                .distinct()
                .join(
                    active_jbs,
                    active_jbs.c.registration_id == emails_union.c.registration_id,
                )
                .where(emails_union.c.email.is_not(None))
            )
        ).all()

        all_results.extend(result)

    return all_results


async def get_inactive_jb_emails() -> list[tuple[str, str]]:
    """Get emails of inactive junior branch members"""
    logging.log(logging.INFO, "Getting inactive JB emails from database")
    all_results: list[tuple[str, str]] = []
    async for sessions in get_async_sessions():
        # Build subquery for getting max expiration date per registration
        max_expiration = (
            select(
                col(MembershipPayments.registration_id),
                func.max(col(MembershipPayments.expiration_date)).label("max_date"),
            )
            .group_by(col(MembershipPayments.registration_id))
            .subquery()
        )

        # Build subquery for inactive JBs based on payments and age
        inactive_jbs = (
            select(col(Registration.registration_id))
            .distinct()
            .outerjoin(
                max_expiration,
                col(Registration.registration_id) == col(max_expiration.c.registration_id),
            )
            .where(
                and_(
                    col(Registration.expelled).is_(False),
                    col(Registration.deceased).is_(False),
                    func.coalesce(max_expiration.c.max_date, text("'1900-01-01'"))
                    < func.current_date(),
                    col(Registration.birth_date)
                    > func.current_date() - text("interval '18 years'"),
                )
            )
            .subquery()
        )

        # Combine emails from both registration emails and legal representatives
        emails_union = (
            select(col(Emails.registration_id), col(Emails.email_address).label("email"))
            .union(
                select(
                    col(LegalRepresentatives.registration_id),
                    col(LegalRepresentatives.email).label("email"),
                )
            )
            .subquery()
        )

        # Final query joining inactive JBs with their emails
        result = (
            await sessions.ro.exec(
                select(emails_union.c.registration_id, emails_union.c.email)
                .distinct()
                .join(
                    inactive_jbs,
                    inactive_jbs.c.registration_id == emails_union.c.registration_id,
                )
                .where(emails_union.c.email.is_not(None))
            )
        ).all()

        all_results.extend(result)

    return all_results
