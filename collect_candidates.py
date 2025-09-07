# collect_candidates.py
# Purpose: Collect candidate users from one or more public groups for manual review.
# WARNING: This script DOES NOT add or message users. It only scrapes participants for ethical manual outreach.

import csv
import asyncio
from telethon import TelegramClient
from telethon.tl.types import UserStatusRecently, UserStatusOnline, UserStatusLastWeek, UserStatusOffline

# ===== CONFIG =====
api_id = 28096799           # Replace with your API ID
api_hash = '0f781ad82b42b382ff9446cdbac9f5bf'  # Replace with your API HASH
session_name = 'session_collect'   # Session filename
source_groups = [
    'infosys_cognizant_accenture_exam',           # group username (not full link)
    'cognizant_tata_elxsi_exam_group',
    'tcs_nqt_exam_accenture_exam'
          # group username (not full link)
]
output_csv = 'candidates.csv'
# ==================

def is_active(status):
    """Return True if user status object indicates recent activity."""
    if status is None:
        return False
    tname = type(status).__name__
    return tname in ('UserStatusOnline', 'UserStatusRecently', 'UserStatusLastWeek')

async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    seen = set()
    rows = []

    for group in source_groups:
        print(f'Fetching participants from {group} ...')
        try:
            participants = await client.get_participants(group)
        except Exception as e:
            print(f'  Error fetching {group}: {e}')
            continue

        for u in participants:
            if getattr(u, 'bot', False) or getattr(u, 'deleted', False):
                continue

            uid = u.id
            if uid in seen:
                continue
            seen.add(uid)

            username = u.username or ''
            name = (u.first_name or '') + (' ' + (u.last_name or '') if u.last_name else '')
            phone = getattr(u, 'phone', '') or ''
            status = getattr(u, 'status', None)

            if username and is_active(status):
                status_label = type(status).__name__ if status else 'unknown'
                rows.append({
                    'user_id': uid,
                    'username': username,
                    'name': name.strip(),
                    'phone': phone,
                    'status': status_label,
                })

    if rows:
        keys = ['user_id', 'username', 'name', 'phone', 'status']
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        print(f'Done. {len(rows)} candidates saved to {output_csv}')
    else:
        print('No candidates found.')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
