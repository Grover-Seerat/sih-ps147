import React from 'react';
import {
  FileSpreadsheet,
  FileText,
  Download,
  Server,
  Info,
  ShieldCheck,
  Activity,
  Cpu,
  Radio,
  BarChart3,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import jsPDF from 'jspdf';

export default function ReportingModule({ activeSignal, onLogAction }) {
  if (!activeSignal) {
    return (
      <div className="p-10 text-center text-slate-500">
        Upload and analyze a signal first.
      </div>
    );
  }

  const sampleRateHz = Number(activeSignal.sampleRateMHz || 0) * 1e6;
  const bandwidthHz = Number(activeSignal.bandwidthMHz || 0) * 1e6;

  const demod = activeSignal.demodulation || {};
  const demodResult = demod.result || {};

  const payload = {
    analysis_id: activeSignal.analysisId,
    file: activeSignal.name,
    format: activeSignal.format,

    classification: {
      modulation: activeSignal.modulation,
      confidence_percent: activeSignal.confidence,
      top_candidates: activeSignal.topCandidates || []
    },

    signal_parameters: {
      sample_rate_hz: sampleRateHz || null,
      bandwidth_hz: bandwidthHz || null,
      snr_db: activeSignal.snrDb,
      symbol_rate_hz: activeSignal.estSymbolRateBaud || null,
      carrier_offset_hz: activeSignal.carrierOffsetHz
    },

    demodulation: {
      status: demod.status || 'Unavailable',
      samples_per_symbol: demodResult.samples_per_symbol ?? null,
      recovered_bits:
        demodResult.num_bits ??
        demodResult.bits?.length ??
        0,
      recovered_audio_samples:
        demodResult.audio?.length ?? null
    },

    evidence: activeSignal.evidence || [],
    dsp_features: activeSignal.dspFeatures || {}
  };

  const download = (content, name, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
  };

  const json = () => {
    download(
      JSON.stringify(payload, null, 2),
      `RF_Analysis_${safeFileName(activeSignal.name)}.json`,
      'application/json'
    );

    onLogAction?.('Exported backend analysis JSON');
  };

  const csv = () => {
    const rows = [
      ['Parameter', 'Value'],
      ['Analysis ID', activeSignal.analysisId],
      ['File', activeSignal.name],
      ['Format', activeSignal.format],
      ['Modulation', activeSignal.modulation],
      ['Confidence %', activeSignal.confidence],
      ['Sample Rate Hz', sampleRateHz || 'N/A'],
      ['Bandwidth Hz', bandwidthHz || 'N/A'],
      ['SNR dB', activeSignal.snrDb ?? 'N/A'],
      ['Symbol Rate Hz', activeSignal.estSymbolRateBaud || 'N/A'],
      ['Carrier Offset Hz', activeSignal.carrierOffsetHz ?? 'N/A'],
      ['Demodulator Status', demod.status || 'Unavailable'],
      [
        'Samples per Symbol',
        demodResult.samples_per_symbol ?? 'N/A'
      ],
      [
        'Recovered Bits',
        demodResult.num_bits ??
          demodResult.bits?.length ??
          0
      ]
    ];

    const csvText = rows
      .map(row => row.map(csvEscape).join(','))
      .join('\n');

    download(
      csvText,
      `RF_Analysis_${safeFileName(activeSignal.name)}.csv`,
      'text/csv'
    );

    onLogAction?.('Exported backend analysis CSV');
  };

  const pdf = () => {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const margin = 16;
    const contentWidth = pageWidth - margin * 2;

    let y = 18;

    // ------------------------------------------------------------------
    // Helper functions
    // ------------------------------------------------------------------

    const addHeader = (title, subtitle = '') => {
      doc.setFillColor(0, 33, 71);
      doc.rect(0, 0, pageWidth, 17, 'F');

      doc.setTextColor(255, 255, 255);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.text('NTRO / SIGINT', margin, 11);

      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.text(
        'RF SIGNAL INTELLIGENCE & ANALYSIS SYSTEM',
        pageWidth - margin,
        11,
        { align: 'right' }
      );

      y = 27;

      doc.setTextColor(0, 33, 71);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.text(title, margin, y);

      if (subtitle) {
        y += 6;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(80, 95, 115);
        doc.text(subtitle, margin, y);
      }

      y += 9;
    };

    const addFooter = () => {
      doc.setDrawColor(210, 218, 230);
      doc.line(margin, pageHeight - 15, pageWidth - margin, pageHeight - 15);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7);
      doc.setTextColor(100, 110, 125);

      doc.text(
        'Generated from uploaded capture using the FastAPI RF analysis backend.',
        margin,
        pageHeight - 9
      );

      doc.text(
        `Page ${doc.internal.getNumberOfPages()}`,
        pageWidth - margin,
        pageHeight - 9,
        { align: 'right' }
      );
    };

    const addSectionTitle = (title, iconText = '') => {
      if (y > pageHeight - 40) {
        addFooter();
        doc.addPage();
        addHeader('RF SIGNAL ANALYSIS REPORT', 'Continued analysis');
      }

      doc.setFillColor(235, 241, 248);
      doc.roundedRect(
        margin,
        y - 5,
        contentWidth,
        9,
        2,
        2,
        'F'
      );

      doc.setTextColor(0, 33, 71);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.text(
        `${iconText ? iconText + '  ' : ''}${title}`,
        margin + 4,
        y + 1
      );

      y += 11;
    };

    const addMetricGrid = (items, columns = 2) => {
      const gap = 5;
      const boxWidth =
        (contentWidth - gap * (columns - 1)) / columns;

      items.forEach((item, index) => {
        const col = index % columns;

        if (col === 0 && index !== 0) {
          y += 22;
        }

        const x = margin + col * (boxWidth + gap);

        if (index === 0 || col === 0) {
          if (y > pageHeight - 40) {
            addFooter();
            doc.addPage();
            addHeader(
              'RF SIGNAL ANALYSIS REPORT',
              'Continued analysis'
            );
          }
        }

        doc.setFillColor(248, 250, 252);
        doc.setDrawColor(220, 226, 235);

        doc.roundedRect(
          x,
          y,
          boxWidth,
          17,
          2,
          2,
          'FD'
        );

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7);
        doc.setTextColor(95, 105, 120);
        doc.text(item.label, x + 4, y + 6);

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(0, 33, 71);

        const value = String(item.value);

        const lines = doc.splitTextToSize(
          value,
          boxWidth - 8
        );

        doc.text(
          lines.slice(0, 2),
          x + 4,
          y + 12
        );
      });

      y += 22;
    };

    const addKeyValueTable = (rows) => {
      const rowHeight = 8;

      rows.forEach(([key, value], index) => {
        if (y > pageHeight - 30) {
          addFooter();
          doc.addPage();
          addHeader(
            'RF SIGNAL ANALYSIS REPORT',
            'Continued analysis'
          );
        }

        if (index % 2 === 0) {
          doc.setFillColor(248, 250, 252);
          doc.rect(
            margin,
            y - 5,
            contentWidth,
            rowHeight,
            'F'
          );
        }

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.setTextColor(70, 85, 105);
        doc.text(String(key), margin + 4, y);

        doc.setFont('helvetica', 'normal');
        doc.setTextColor(20, 35, 55);

        const valueLines = doc.splitTextToSize(
          formatValue(value),
          contentWidth - 70
        );

        doc.text(
          valueLines.slice(0, 2),
          margin + 65,
          y
        );

        y += rowHeight;
      });

      y += 3;
    };

    const addBulletList = (items) => {
      items.forEach(item => {
        if (y > pageHeight - 30) {
          addFooter();
          doc.addPage();
          addHeader(
            'RF SIGNAL ANALYSIS REPORT',
            'Continued analysis'
          );
        }

        const lines = doc.splitTextToSize(
          String(item),
          contentWidth - 10
        );

        doc.setFillColor(0, 80, 150);
        doc.circle(margin + 2, y - 1.5, 0.8, 'F');

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(45, 55, 70);

        doc.text(
          lines,
          margin + 6,
          y
        );

        y += Math.max(6, lines.length * 4.5);
      });

      y += 2;
    };

    const addText = (text, size = 8) => {
      const lines = doc.splitTextToSize(
        String(text),
        contentWidth
      );

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(size);
      doc.setTextColor(55, 65, 80);

      doc.text(lines, margin, y);

      y += lines.length * (size <= 8 ? 4 : 5) + 3;
    };

    // ------------------------------------------------------------------
    // PAGE 1 — COVER / EXECUTIVE SUMMARY
    // ------------------------------------------------------------------

    doc.setFillColor(0, 33, 71);
    doc.rect(0, 0, pageWidth, 48, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text('NTRO / SIGINT', margin, 15);

    doc.setFontSize(21);
    doc.text('RF SIGNAL', margin, 29);
    doc.text('ANALYSIS REPORT', margin, 39);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text(
      'Automated RF signal intelligence and modulation analysis',
      pageWidth - margin,
      38,
      { align: 'right' }
    );

    y = 61;

    doc.setTextColor(0, 33, 71);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text('EXECUTIVE SUMMARY', margin, y);

    y += 8;

    // Primary finding box
    doc.setFillColor(241, 247, 253);
    doc.setDrawColor(150, 175, 205);

    doc.roundedRect(
      margin,
      y,
      contentWidth,
      38,
      3,
      3,
      'FD'
    );

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(85, 100, 120);
    doc.text('PRIMARY MODULATION CLASSIFICATION', margin + 6, y + 9);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(24);
    doc.setTextColor(0, 50, 130);
    doc.text(
      String(activeSignal.modulation || 'UNKNOWN').toUpperCase(),
      margin + 6,
      y + 23
    );

    doc.setFontSize(10);
    doc.setTextColor(55, 70, 90);
    doc.text(
      `Model confidence: ${activeSignal.confidence ?? 'N/A'}%`,
      margin + 6,
      y + 31
    );

    y += 48;

    addMetricGrid([
      {
        label: 'FILE',
        value: activeSignal.name
      },
      {
        label: 'ANALYSIS ID',
        value: activeSignal.analysisId
      },
      {
        label: 'SAMPLE RATE',
        value: sampleRateHz
          ? formatFrequency(sampleRateHz)
          : 'N/A'
      },
      {
        label: 'BANDWIDTH',
        value: bandwidthHz
          ? formatFrequency(bandwidthHz)
          : 'N/A'
      },
      {
        label: 'SNR',
        value:
          activeSignal.snrDb != null
            ? `${activeSignal.snrDb} dB`
            : 'N/A'
      },
      {
        label: 'CARRIER OFFSET',
        value:
          activeSignal.carrierOffsetHz != null
            ? `${activeSignal.carrierOffsetHz} Hz`
            : 'N/A'
      }
    ]);

    addSectionTitle('SIGNAL OVERVIEW', '01');

    addKeyValueTable([
      ['File name', activeSignal.name],
      ['Input format', activeSignal.format || 'IQ/WAV'],
      ['Analysis timestamp', activeSignal.timestamp || 'N/A'],
      ['Modulation', activeSignal.modulation || 'Unknown'],
      [
        'Confidence',
        activeSignal.confidence != null
          ? `${activeSignal.confidence}%`
          : 'N/A'
      ],
      [
        'Sample rate',
        sampleRateHz
          ? `${sampleRateHz.toLocaleString()} Hz`
          : 'N/A'
      ],
      [
        'Bandwidth',
        bandwidthHz
          ? `${bandwidthHz.toLocaleString()} Hz`
          : 'N/A'
      ],
      [
        'Estimated symbol rate',
        activeSignal.estSymbolRateBaud
          ? `${Number(activeSignal.estSymbolRateBaud).toLocaleString()} Hz`
          : 'N/A'
      ]
    ]);

    // ------------------------------------------------------------------
    // PAGE 2 — DSP ANALYSIS
    // ------------------------------------------------------------------

    addFooter();
    doc.addPage();

    addHeader(
      'DSP & SIGNAL PARAMETERS',
      'Backend-derived signal measurements'
    );

    addSectionTitle('SIGNAL QUALITY', '02');

    addMetricGrid([
      {
        label: 'SNR',
        value:
          activeSignal.snrDb != null
            ? `${activeSignal.snrDb} dB`
            : 'N/A'
      },
      {
        label: 'BANDWIDTH',
        value: bandwidthHz
          ? formatFrequency(bandwidthHz)
          : 'N/A'
      },
      {
        label: 'CARRIER OFFSET',
        value:
          activeSignal.carrierOffsetHz != null
            ? `${activeSignal.carrierOffsetHz} Hz`
            : 'N/A'
      },
      {
        label: 'SYMBOL RATE',
        value: activeSignal.estSymbolRateBaud
          ? `${Number(activeSignal.estSymbolRateBaud).toLocaleString()} Hz`
          : 'N/A'
      }
    ]);

    addSectionTitle('BACKEND DSP FEATURES', '03');

    const featureRows = Object.entries(
      activeSignal.dspFeatures || {}
    );

    if (featureRows.length) {
      addKeyValueTable(
        featureRows.map(([key, value]) => [
          humanizeKey(key),
          formatValue(value)
        ])
      );
    } else {
      addText(
        'No additional DSP feature values were returned by the backend.'
      );
    }

    // ------------------------------------------------------------------
    // PAGE 3 — ML CLASSIFICATION
    // ------------------------------------------------------------------

    addFooter();
    doc.addPage();

    addHeader(
      'MACHINE LEARNING CLASSIFICATION',
      'Backend Random Forest modulation classifier'
    );

    addSectionTitle('PRIMARY CLASSIFICATION', '04');

    addMetricGrid([
      {
        label: 'MODEL',
        value: 'Random Forest'
      },
      {
        label: 'FEATURE COUNT',
        value: '23 DSP-derived features'
      },
      {
        label: 'PREDICTION',
        value: activeSignal.modulation || 'Unknown'
      },
      {
        label: 'CONFIDENCE',
        value:
          activeSignal.confidence != null
            ? `${activeSignal.confidence}%`
            : 'N/A'
      }
    ]);

    addSectionTitle('TOP MODEL CANDIDATES', '05');

    const candidates = activeSignal.topCandidates || [];

    if (candidates.length) {
      candidates.forEach((candidate, index) => {
        const label =
          candidate.label ||
          candidate.modulation ||
          candidate.class ||
          `Candidate ${index + 1}`;

        const probability =
          candidate.confidence ??
          candidate.probability ??
          candidate.score;

        const pct =
          probability != null
            ? probability <= 1
              ? probability * 100
              : probability
            : null;

        if (y > pageHeight - 25) {
          addFooter();
          doc.addPage();
          addHeader(
            'MACHINE LEARNING CLASSIFICATION',
            'Continued candidate analysis'
          );
        }

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.setTextColor(45, 60, 80);

        doc.text(
          `${index + 1}. ${label}`,
          margin,
          y
        );

        const barX = margin + 50;
        const barWidth = contentWidth - 80;

        doc.setFillColor(225, 231, 240);
        doc.roundedRect(
          barX,
          y - 4,
          barWidth,
          4,
          1,
          1,
          'F'
        );

        if (pct != null) {
          doc.setFillColor(0, 90, 170);

          doc.roundedRect(
            barX,
            y - 4,
            Math.max(
              1,
              barWidth * Math.min(100, Math.max(0, pct)) / 100
            ),
            4,
            1,
            1,
            'F'
          );

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(7);
          doc.text(
            `${pct.toFixed(1)}%`,
            pageWidth - margin,
            y,
            { align: 'right' }
          );
        }

        y += 10;
      });
    } else {
      addText(
        'The backend did not return a top-candidate probability list.'
      );
    }

    addSectionTitle('CLASSIFICATION INTERPRETATION', '06');

    addText(
      `The uploaded signal was processed through the backend DSP feature-extraction pipeline and classified using the Random Forest modulation model. The reported modulation is ${activeSignal.modulation || 'Unknown'} with a model confidence of ${activeSignal.confidence ?? 'N/A'}%.`
    );

    // ------------------------------------------------------------------
    // PAGE 4 — DEMODULATION
    // ------------------------------------------------------------------

    addFooter();
    doc.addPage();

    addHeader(
      'DEMODULATION & CONSTELLATION',
      'Backend demodulation result'
    );

    addSectionTitle('DEMODULATION STATUS', '07');

    const demodSuccessful =
      String(demod.status || '').toLowerCase() === 'success';

    addMetricGrid([
      {
        label: 'MODULATION',
        value: activeSignal.modulation || 'Unknown'
      },
      {
        label: 'DEMODULATOR',
        value: demod.status || 'Unavailable'
      },
      {
        label: 'CARRIER OFFSET',
        value:
          activeSignal.carrierOffsetHz != null
            ? `${activeSignal.carrierOffsetHz} Hz`
            : 'N/A'
      },
      {
        label: 'SAMPLES / SYMBOL',
        value:
          demodResult.samples_per_symbol ?? 'N/A'
      },
      {
        label: 'RECOVERED BITS',
        value:
          demodResult.num_bits ??
          demodResult.bits?.length ??
          0
      },
      {
        label: 'RECOVERED AUDIO SAMPLES',
        value:
          demodResult.audio?.length ??
          'N/A'
      }
    ]);

    const statusText = demodSuccessful
      ? 'Demodulation completed successfully using the backend-selected modulation.'
      : 'Demodulation was not reported as successful by the backend.';

    doc.setFillColor(
      demodSuccessful ? 239 : 254,
      demodSuccessful ? 250 : 242,
      demodSuccessful ? 244 : 242
    );

    doc.setDrawColor(
      demodSuccessful ? 150 : 220,
      demodSuccessful ? 200 : 180,
      demodSuccessful ? 170 : 180
    );

    doc.roundedRect(
      margin,
      y,
      contentWidth,
      24,
      3,
      3,
      'FD'
    );

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.setTextColor(0, 33, 71);

    doc.text(
      demodSuccessful
        ? '✓ BACKEND DEMODULATION SUCCESS'
        : '⚠ BACKEND DEMODULATION STATUS',
      margin + 6,
      y + 9
    );

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(65, 75, 90);

    const statusLines = doc.splitTextToSize(
      statusText,
      contentWidth - 12
    );

    doc.text(
      statusLines,
      margin + 6,
      y + 16
    );

    y += 33;

    addSectionTitle('RECOVERED DATA', '08');

    addKeyValueTable([
      [
        'Recovered bits',
        demodResult.num_bits ??
          demodResult.bits?.length ??
          0
      ],
      [
        'Samples per symbol',
        demodResult.samples_per_symbol ?? 'N/A'
      ],
      [
        'Recovered audio samples',
        demodResult.audio?.length ?? 'N/A'
      ]
    ]);

    // ------------------------------------------------------------------
    // PAGE 5 — EVIDENCE
    // ------------------------------------------------------------------

    addFooter();
    doc.addPage();

    addHeader(
      'EVIDENCE & BACKEND DECISION',
      'Supporting information returned by the analysis pipeline'
    );

    addSectionTitle('ANALYSIS EVIDENCE', '09');

    const evidence = activeSignal.evidence || [];

    if (evidence.length) {
      addBulletList(
        evidence.map(item => {
          if (typeof item === 'string') return item;

          if (item && typeof item === 'object') {
            const key =
              item.feature ||
              item.name ||
              item.type ||
              'Evidence';

            const value =
              item.value ??
              item.description ??
              item.message ??
              '';

            return `${humanizeKey(key)}: ${formatValue(value)}`;
          }

          return String(item);
        })
      );
    } else {
      addText(
        'No additional evidence statements were returned by the backend.'
      );
    }

    addSectionTitle('DECISION SUMMARY', '10');

    addText(
      `Final backend classification: ${activeSignal.modulation || 'Unknown'}.`
    );

    addText(
      `Reported classifier confidence: ${activeSignal.confidence ?? 'N/A'}%.`
    );

    addText(
      `The report reflects the selected backend analysis session identified by ${activeSignal.analysisId || 'N/A'}. Frontend-generated synthetic signal values are not used in this report.`
    );

    // ------------------------------------------------------------------
    // PAGE 6 — METHODOLOGY
    // ------------------------------------------------------------------

    addFooter();
    doc.addPage();

    addHeader(
      'TECHNICAL METHODOLOGY',
      'RF analysis processing chain'
    );

    addSectionTitle('BACKEND PROCESSING PIPELINE', '11');

    const pipeline = [
      'IQ / WAV signal upload',
      'Universal signal reader and preprocessing',
      'DSP analysis and signal parameter estimation',
      'Extraction of 23 engineered RF/DSP features',
      'Random Forest modulation classification',
      'Backend evidence evaluation',
      'Modulation-specific demodulation',
      'Analysis result exposed to the frontend'
    ];

    pipeline.forEach((step, index) => {
      if (y > pageHeight - 35) {
        addFooter();
        doc.addPage();
        addHeader(
          'TECHNICAL METHODOLOGY',
          'Continued methodology'
        );
      }

      doc.setFillColor(0, 33, 71);
      doc.circle(margin + 5, y - 2, 4, 'F');

      doc.setTextColor(255, 255, 255);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(7);
      doc.text(
        String(index + 1),
        margin + 5,
        y + 0.5,
        { align: 'center' }
      );

      doc.setTextColor(45, 55, 70);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8);
      doc.text(step, margin + 14, y);

      if (index < pipeline.length - 1) {
        doc.setDrawColor(180, 195, 215);
        doc.line(
          margin + 5,
          y + 3,
          margin + 5,
          y + 9
        );
      }

      y += 12;
    });

    addSectionTitle('WHY RANDOM FOREST', '12');

    addBulletList([
      'Designed for nonlinear relationships among engineered RF/DSP features.',
      'Suitable for structured tabular feature data rather than requiring raw IQ deep learning.',
      'Robust to noisy and interacting signal features.',
      'Provides feature-importance information for interpretability.',
      'Fast inference is suitable for an automated backend analysis workflow.',
      'Benchmark comparison showed the strongest overall performance among the evaluated classifiers.'
    ]);

    addSectionTitle('MODEL BENCHMARK', '13');

    addKeyValueTable([
      ['Random Forest', '76.35% test accuracy / 0.762 Macro F1'],
      ['HistGradientBoosting', '76.15% test accuracy / 0.761 Macro F1'],
      ['Extra Trees', '73.96% test accuracy / 0.736 Macro F1'],
      ['SVM RBF', '67.81% test accuracy / 0.672 Macro F1']
    ]);

    // ------------------------------------------------------------------
    // FINAL FOOTER
    // ------------------------------------------------------------------

    addFooter();

    doc.save(
      `RF_Analysis_${safeFileName(activeSignal.name)}.pdf`
    );

    onLogAction?.('Exported professional backend analysis PDF');
  };

  return (
    <div className="p-6 space-y-6 font-mono">

      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h2 className="text-lg font-extrabold text-[#002147] flex items-center">
          <FileSpreadsheet className="w-5 h-5 mr-2" />
          REPORTING & EXPORT
        </h2>

        <p className="text-xs text-slate-600 mt-1">
          Generate a structured technical report from the selected
          backend analysis session.
        </p>
      </div>

      {/* Export buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        <Card
          icon={<FileText />}
          title="Professional PDF Report"
        >
          <button
            onClick={pdf}
            className="w-full py-2.5 rounded-lg bg-[#002147] text-white text-xs font-bold hover:bg-[#003665] transition"
          >
            Download PDF
          </button>
        </Card>

        <Card
          icon={<Download />}
          title="Machine-readable JSON"
        >
          <button
            onClick={json}
            className="w-full py-2.5 rounded-lg bg-[#002147] text-white text-xs font-bold hover:bg-[#003665] transition"
          >
            Export JSON
          </button>
        </Card>

        <Card
          icon={<FileSpreadsheet />}
          title="CSV Summary"
        >
          <button
            onClick={csv}
            className="w-full py-2.5 rounded-lg bg-[#002147] text-white text-xs font-bold hover:bg-[#003665] transition"
          >
            Export CSV
          </button>
        </Card>

      </div>

      {/* Evidence notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start">
        <Info className="w-4 h-4 mr-2 mt-0.5 shrink-0" />

        <span>
          Reports are generated from the selected backend analysis.
          No synthetic frontend signal values are inserted into the
          report.
        </span>
      </div>

      {/* Current backend result */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">

        <h3 className="font-extrabold text-[#002147] flex items-center">
          <Server className="w-4 h-4 mr-2" />
          CURRENT BACKEND ANALYSIS
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">

          <SummaryCard
            icon={<Radio />}
            label="MODULATION"
            value={activeSignal.modulation || 'Unknown'}
          />

          <SummaryCard
            icon={<Activity />}
            label="CONFIDENCE"
            value={
              activeSignal.confidence != null
                ? `${activeSignal.confidence}%`
                : 'N/A'
            }
          />

          <SummaryCard
            icon={<BarChart3 />}
            label="SNR"
            value={
              activeSignal.snrDb != null
                ? `${activeSignal.snrDb} dB`
                : 'N/A'
            }
          />

          <SummaryCard
            icon={<Cpu />}
            label="MODEL"
            value="Random Forest"
          />

        </div>

        <pre className="mt-5 bg-slate-50 border rounded p-4 text-[11px] overflow-auto max-h-[420px]">
          {JSON.stringify(payload, null, 2)}
        </pre>

      </div>

    </div>
  );
}


// ----------------------------------------------------------------------
// UI COMPONENTS
// ----------------------------------------------------------------------

function Card({ icon, title, children }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
      <h3 className="font-extrabold text-[#002147] flex items-center">
        {React.cloneElement(icon, {
          className: 'w-5 h-5 mr-2 text-blue-700'
        })}
        {title}
      </h3>

      {children}
    </div>
  );
}

function SummaryCard({ icon, label, value }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">

      <div className="flex items-center text-[10px] font-extrabold text-slate-500">
        {React.cloneElement(icon, {
          className: 'w-4 h-4 mr-2 text-blue-700'
        })}
        {label}
      </div>

      <div className="mt-2 text-lg font-extrabold text-[#002147]">
        {String(value)}
      </div>

    </div>
  );
}


// ----------------------------------------------------------------------
// HELPERS
// ----------------------------------------------------------------------

function safeFileName(name) {
  return String(name || 'signal')
    .replace(/\.[^/.]+$/, '')
    .replace(/[^a-zA-Z0-9_-]+/g, '_')
    .slice(0, 80);
}

function csvEscape(value) {
  const text = String(value ?? '');

  if (
    text.includes(',') ||
    text.includes('"') ||
    text.includes('\n')
  ) {
    return `"${text.replace(/"/g, '""')}"`;
  }

  return text;
}

function humanizeKey(key) {
  return String(key)
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'N/A';
  }

  if (typeof value === 'number') {
    return Number.isFinite(value)
      ? value.toLocaleString(undefined, {
          maximumFractionDigits: 6
        })
      : 'N/A';
  }

  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  return String(value);
}

function formatFrequency(hz) {
  const value = Number(hz);

  if (!Number.isFinite(value)) {
    return 'N/A';
  }

  if (Math.abs(value) >= 1e9) {
    return `${(value / 1e9).toFixed(3)} GHz`;
  }

  if (Math.abs(value) >= 1e6) {
    return `${(value / 1e6).toFixed(3)} MHz`;
  }

  if (Math.abs(value) >= 1e3) {
    return `${(value / 1e3).toFixed(3)} kHz`;
  }

  return `${value.toFixed(2)} Hz`;
}