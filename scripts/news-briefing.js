const nodemailer = require('nodemailer');

const companies = [
  '삼성전자', '네이버', 'KT&G', 'KT', 'SKT', '한화에어로스페이스',
  '현대자동차', '기아자동차', '현대모비스', '현대글로비스', '포스코',
  '포스코홀딩스', 'SK하이닉스', '두산밥캣', 'KCC', 'GS칼텍스',
  '한화토탈에너지스', 'S-oil', '엘지화학', '엘지에너지솔루션',
  'SK이노베이션', 'SK Inc', '한국전력', '한국수자원공사',
  '한국석유공사', '한국가스공사', '인천공항공사', '한수원',
  '포스코인터네셔널', '삼성물산', '광해광업공단'
];

async function getNews(company) {
  try {
    const url = `https://news.google.com/rss/search?q=${encodeURIComponent(company + ' 뉴스')}&hl=ko&gl=KR&ceid=KR:ko`;
    const response = await fetch(url);
    const text = await response.text();
    
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    let match;
    
    while ((match = itemRegex.exec(text)) !== null && items.length < 3) {
      const itemContent = match[1];
      const title = itemContent.match(/<title>(.*?)<\/title>/)?.[1] || '';
      const link = itemContent.match(/<link>(.*?)<\/link>/)?.[1] || '';
      const pubDate = itemContent.match(/<pubDate>(.*?)<\/pubDate>/)?.[1] || '';
      
      if (title) {
        items.push({ title: title.replace(/<!\[CDATA\[|\]\]>/g, ''), link, pubDate });
      }
    }
    
    return items;
  } catch (error) {
    console.error(`Error fetching news for ${company}:`, error.message);
    return [];
  }
}

function formatDate() {
  const now = new Date();
  return now.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
}

async function main() {
  console.log('Starting news briefing...');
  
  let htmlContent = `
    <h2>📅 일일 기업 뉴스 브리핑 - ${formatDate()}</h2>
    <h3>🔴 주요 이슈</h3>
    <p>오늘의 커버 기업 뉴스입니다.</p>
    <hr>
    <h3>📊 기업별 뉴스</h3>
  `;
  
  for (const company of companies) {
    console.log(`Fetching news for ${company}...`);
    const news = await getNews(company);
    
    htmlContent += `<h4>${company}</h4>`;
    
    if (news.length === 0) {
      htmlContent += `<p>오늘 별도 뉴스 없음</p>`;
    } else {
      htmlContent += '<ul>';
      for (const item of news) {
        htmlContent += `<li><b>${item.title}</b></li>`;
      }
      htmlContent += '</ul>';
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  htmlContent += `
    <hr>
    <p><i>이 뉴스는 자동으로 수집 및 정리되었습니다.</i></p>
  `;
  
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'williamai762@gmail.com',
      pass: process.env.GMAIL_APP_PASSWORD
    }
  });
  
  const mailOptions = {
    from: 'williamai762@gmail.com',
    to: 'williamai762@gmail.com',
    subject: `[일일 뉴스 브리핑] 커버 기업 뉴스 정리 - ${formatDate()}`,
    html: htmlContent
  };
  
  try {
    await transporter.sendMail(mailOptions);
    console.log('Email sent successfully!');
  } catch (error) {
    console.error('Error sending email:', error);
    process.exit(1);
  }
}

main();
