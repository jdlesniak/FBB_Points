 FBB_Points

**Custom Fantasy Baseball Points Projections Using ZiPS**

A customizable tool to help fantasy baseball managers estimate player value using FanGraphs ZiPS projections and any league-specific scoring system.

---

## Overview

Every year, millions of fantasy baseball managers prepare for their drafts by researching player stats, trends, and projections. This project helps streamline that process by allowing users to calculate custom fantasy point totals for players based on **your own scoring rules**, using **ZiPS** as the projection source.

Note: This repository does **not** include player projection data. FanGraphs requires a subscription to download ZiPS data, and redistribution is not permitted.

---

## Project Purpose

This project is designed to:

- Translate ZiPS projections into fantasy point estimates
- Allow full customization of scoring rules
- Provide a repeatable, transparent workflow for evaluating player value

Whether you're preparing for a draft or managing your roster mid-season, this tool helps surface value and risk based on actual projected outcomes.

---

## Data Source

The data comes from **ZiPS projections** by Dan Szymborski, available via [FanGraphs](https://www.fangraphs.com). These projections represent the **median outcome** from a distribution of simulations for each player.

While medians offer a stable and interpretable estimate, they may not fully reflect volatility. For example, the figure below illustrates a bimodal distribution where the median outcome is unlikely to occur.

![BiModal](https://github.com/user-attachments/assets/e07814ac-f84f-4563-8e87-6e9583952584)

This type of distribution might represent a highly talented but injury-prone player. If they stay healthy, they produce; if not, they underperform. The median is a compromise between those extremes.

Despite these limitations, we rely on the median because it's the value ZiPS provides, and it serves as a fair baseline for consistent scoring estimates.

---

## Blown Saves Exception

ZiPS does not include a projection for **blown saves**, a stat that often results in negative points in many leagues. To account for this, I implemented a simple model to predict blown saves based on available data. You're welcome to review, critique, or improve that approach.

---

## Data Licensing

This project does not provide any ZiPS projection data.

- FanGraphs requires a paid membership to access these projections.
- Redistribution of their data violates their terms of service.
- As of writing, a 30-day membership costs $10.
- I strongly encourage supporting FanGraphs and Dan Szymborski’s work by subscribing.

---

## Using the App

You can try the live version of the app here:

**[Live Streamlit App](https://fbbpoints-jlesniak-public.streamlit.app/)**
