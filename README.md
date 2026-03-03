## Geopolitical Alpha: Oil Trading & Backtesting Engine

An Event-Driven Quantitative Strategy linking Global Conflict News with Physical Supply and Market Price Action.




## Project Overview

This repository contains a full-stack quantitative research pipeline designed to trade the United States Oil Fund ($USO). Unlike standard technical analysis bots, this engine uses a "triangulation" method—verifying price trends against real-world geopolitical events and physical supply data.



## The Data Architecture
The engine orchestrates three distinct data streams to try to create a high-conviction trading signal:

Geopolitical Sentiment (GDELT Project) -> Data is queried via Google BigQuery using SQL to analyze millions of global news records. It calculates a daily "Conflict Score" based on Material Conflict events (Event Codes 18, 19, 20) in key oil-producing regions.

Physical Fundamentals (EIA API) -> The engine fetches weekly Crude Oil Inventory levels directly from the U.S. Energy Information Administration to detect supply/demand imbalances.

Market Action (Yahoo Finance) -> Fetches daily OHLCV data for $USO to execute trades based on Moving Average crossovers and volatility filters.



## Tech Stack
Language -> Python 3.10+

Backtesting -> Backtrader (Event-driven engine)

Data Science -> Pandas, NumPy

Cloud -> Google BigQuery (GDELT Dataset)

APIs -> EIA Open Data v2, yfinance



## Performance & The "Overfitting" Lesson
During the AI Optimization phase, the engine identified a parameter set yielding a ~91% return over a 3-year period.

Quantitative Mat. Note -> While the returns appear high, this project serves as a case study in overfitting. The optimizer achieved these results by identifying a hyper-specific set of historical "lucky" trades. True quantitative success requires out-of-sample testing and robust risk management, which are the primary focus of this research tool.



## Setup & Installation
Clone the repo -> git clone https://github.com/estevaoabreupeixoto/oil_strat_wip.git

Add the credentials -> Place your google_key.json in the root directory (ignored by .gitignore).

Add your EIA API Key to the MY_EIA_KEY variable in main.py.

Run the Engine -> python main.py
