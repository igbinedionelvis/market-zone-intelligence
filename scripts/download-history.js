const { spawn } = require("child_process");
const { spawnSync } = require("child_process");

const args = process.argv.slice(2);

if (args.length !== 2) {
  console.error(
    "Usage: npm run download:history -- <start-date> <end-date>"
  );
  process.exit(1);
}

const [startDate, endDate] = args;
const datePattern = /^\d{4}-\d{2}-\d{2}$/;

if (!datePattern.test(startDate) || !datePattern.test(endDate)) {
  console.error("Dates must use YYYY-MM-DD format.");
  process.exit(1);
}

if (startDate >= endDate) {
  console.error("End date must be after start date.");
  process.exit(1);
}

function addDays(date, days) {
  const result = new Date(`${date}T00:00:00Z`);
  result.setUTCDate(result.getUTCDate() + days);
  return result.toISOString().slice(0, 10);
}

function downloadBatch(from, to) {
  const commandArgs = [
    "--instrument", "eurusd",
    "--date-from", from,
    "--date-to", to,
    "--timeframe", "m15",
    "--price-type", "bid",
    "--utc-offset", "0",
    "--format", "csv",
    "--directory", "./data/raw",
    "--retries", "3",
  ];

  console.log(`\nDownloading batch: ${from} to ${to}`);

  return new Promise((resolve, reject) => {
    const downloader = spawn(
      "npx",
      ["dukascopy-node", ...commandArgs],
      {
        stdio: "inherit",
        shell: true,
      }
    );

    downloader.on("error", reject);

    downloader.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(
          new Error(`Download failed for ${from} to ${to}`)
        );
      }
    });
  });
}

async function main() {
  let currentDate = startDate;

  while (currentDate < endDate) {
    const nextDate = addDays(currentDate, 7);
    const batchEnd = nextDate < endDate ? nextDate : endDate;

    await downloadBatch(currentDate, batchEnd);

    currentDate = batchEnd;
  }

  console.log("\nAll download batches completed.");
  console.log("\nRunning dataset validator...");

  const validator = spawnSync(
    ".\\backend\\.venv\\Scripts\\python.exe",
    ["backend\\scripts\\validate_historical_ohlc.py"],
    {
      stdio: "inherit",
      shell: true,
    }
  );

  if (validator.status !== 0) {
    console.error("\nDataset validation failed.");
    process.exit(1);
  }

  console.log("\nDownload and validation completed successfully.");
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});