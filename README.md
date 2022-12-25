# Backend for Random Tech Tweet Generator

## What is this?
This is a backend for [Fetch Random Tech Tweet](https://github.com/Dibakarroy1997/fetch-random-tech-tweet) application. This repository is automatically updated using [git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action).

## How it works?

- It uses Twitter API to fetch latest tweets from users defined under [assets/config.yml](assets/config.yml) file.
- Each user have category of tweet define under them. Each category has a name and a regex which will be used to determine if a tweet falls under a specific category. If a tweet doesn't fall under specified categories defined in the config file then it is considered as 'Others' category.
- Once every 5 min (or more as per the GitHub action job schedule preference), we will use the Twitter API to fetch latest tweets from the users in config file and update a database.
- At the end this database is converted into JSON and pushed in the same repository.
- This JSON is used to host a REST API using [json-server](https://github.com/typicode/json-server). API is hosted using [Vercel](https://vercel.com/dashboard) using [json-server-vercel](https://github.com/kitloong/json-server-vercel) template.

> Link to REST endpoint: https://fetch-random-tech-tweet-backend.vercel.app/