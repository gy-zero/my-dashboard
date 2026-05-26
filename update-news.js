const fs = require('fs');

async function main() {
  const now = new Date().toISOString();

  let current = [];
  if (fs.existsSync('news.json')) {
    try {
      current = JSON.parse(fs.readFileSync('news.json', 'utf8'));
      if (!Array.isArray(current)) current = [];
    } catch (e) {
      current = [];
    }
  }

  const newItem = {
    title: `Auto update ${now}`,
    link: 'https://gy-zero.github.io/my-dashboard/',
    source: 'GitHub Actions',
    publishedAt: now
  };

  current.unshift(newItem);
  current = current.slice(0, 20);

  fs.writeFileSync('news.json', JSON.stringify(current, null, 2) + '\n');
  console.log('news.json updated');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
