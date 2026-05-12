// 화면 캡처 기반 PDF 저장. 한글 폰트 문제를 피하기 위해 캔버스 이미지로 변환.

import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { todayStr } from './formatters.js';

export async function exportElementToPdf(element, stockName, stockCode) {
  if (!element) {
    throw new Error('PDF 대상 요소를 찾을 수 없습니다.');
  }

  // 모바일에서 안정성을 위해 scale 제한
  const scale = Math.min(2, window.devicePixelRatio || 1.5);

  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale,
    useCORS: true,
    logging: false,
    windowWidth: element.scrollWidth,
    windowHeight: element.scrollHeight,
  });

  const imgData = canvas.toDataURL('image/jpeg', 0.92);

  // A4 세로
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();

  const imgW = pageW;
  const imgH = (canvas.height * imgW) / canvas.width;

  let heightLeft = imgH;
  let position = 0;

  pdf.addImage(imgData, 'JPEG', 0, position, imgW, imgH);
  heightLeft -= pageH;

  while (heightLeft > 0) {
    position = heightLeft - imgH;
    pdf.addPage();
    pdf.addImage(imgData, 'JPEG', 0, position, imgW, imgH);
    heightLeft -= pageH;
  }

  const safeName = (stockName || '종목').replace(/[\\/:*?"<>|]/g, '');
  const filename = `${safeName}_${stockCode}_분석리포트_${todayStr()}.pdf`;
  pdf.save(filename);

  return filename;
}
