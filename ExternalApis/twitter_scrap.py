import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level


async def main():
    api = API()  # or API("path-to.db") - default is `accounts.db`
    # ADD ACCOUNTS (for CLI usage see BELOW)
    await api.pool.add_account("", "", "@gmail.com", "")
    await api.pool.login_all()

    # get user by login
    user_login = "HollowPoiint"
    # change log level, default info
    set_log_level("DEBUG")

    # Tweet & User model can be converted to regular dict or json, e.g.:
    doc = await api.user_by_login(user_login)  # User
    doc.dict()  # -> python dict
    print(doc.dict())


if __name__ == "__main__":
    asyncio.run(main())
