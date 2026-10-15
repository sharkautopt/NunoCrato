"""Build the updated CV PDF (docs/documents/cv/nuno-crato-cv-2026.pdf). Edit the data below, then run tools/build.sh.
Based on the 2023 CV plus 2024-2026 items already published on the site."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

OUT = "docs/documents/cv/nuno-crato-cv-2026.pdf"
FOREST = colors.HexColor("#1c4532")
base = ParagraphStyle("b", fontName="Times-Roman", fontSize=10, leading=13)
h1 = ParagraphStyle("h1", fontName="Times-Bold", fontSize=22, leading=26, textColor=FOREST)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=FOREST, spaceBefore=11, spaceAfter=4)
sm = ParagraphStyle("s", parent=base, fontSize=9.5, leading=12.5)
pub = ParagraphStyle("p", parent=base, fontSize=9.5, leading=12.3, leftIndent=12, firstLineIndent=-12, spaceAfter=2.5)
when = ParagraphStyle("w", parent=base, fontName="Times-Bold", fontSize=9.5)

def sec(title): return [Paragraph(title.upper(), h2)]
def rows(items):
    t = Table([[Paragraph(a, when), Paragraph(b, sm)] for a, b in items], colWidths=[26*mm, 144*mm])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5), ("TOPPADDING", (0,0), (-1,-1), 0), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
    return [t]
def pubs(items): return [Paragraph(x, pub) for x in items]

s = []
s += [Paragraph("Nuno Crato", h1), Spacer(1, 3),
      Paragraph("Professor Catedrático (Full Professor) of Statistics and Econometrics<br/>ISEG, Lisbon School of Economics &amp; Management, University of Lisbon<br/>R. do Quelhas 6, 1200-781 Lisbon, Portugal", base), Spacer(1, 4),
      Paragraph("ncrato@iseg.ulisboa.pt · ncrato@gmail.com · www.nunocrato.org", base),
      Paragraph("Updated October 2026", ParagraphStyle("u", parent=base, fontSize=8.5, textColor=colors.grey))]

s += sec("Current and recent positions and services")
s += rows([
 ("2010–", "Professor, Department of Mathematics, ISEG, University of Lisbon; researcher at CEMAPRE/REM."),
 ("2016–", "Visiting senior research scientist, European Commission Joint Research Centre."),
 ("2019–2026", "Founding president, Iniciativa Educação, a charity dedicated to students' education."),
 ("2019–", "Board member, Fundação Francisco Manuel dos Santos."),
 ("2021–", "Member, RCQE–UNESCO Advising Committee."),
 ("2020–", "External consultant, World Bank and BAIN."),
 ("2018–", "Adviser, Education and Human Resources Council, United Arab Emirates."),
 ("Current", "Member, Scientific Council for National Education (CSEN), French Ministry of Education."),
 ("2011–2015", "Minister of Education and Science, Portuguese Republic."),
 ("2010–2011", "CEO, Taguspark, S.A., Science and Technology Park."),
 ("2007–2011", "Dean (Pró-reitor) for Scientific Culture, Lisbon Technical University."),
 ("2007–2010", "President and scientific coordinator, Cemapre Research Center, ISEG."),
 ("2004–2010", "President, Portuguese Mathematical Society (SPM)."),
 ("1993–1994", "External consultant, World Bank."),
 ("1985–1988", "Technical Director for consulting, Norma-Açores."),
])
s += sec("Research interests")
s += [Paragraph("Econometrics, time-series analysis, probability models and applications, and the economics and statistics of education, including data-based evaluation of public policy.", sm)]

s += sec("Education")
s += rows([
 ("2002", "Aggregation (Habilitation), Lisbon Technical University."),
 ("1992", "Ph.D. in Applied Mathematics, University of Delaware. Dissertation: “On some misspecification problems in long-memory fractional time series models”; advisor Prof. Howard M. Taylor."),
 ("1985", "M.S. (mestrado) in Mathematical Methods for Management Decisions, Technical University of Lisbon. Thesis on Kalman-filter prediction; adviser Prof. Daniel Muller."),
 ("1981", "B.S. (licenciatura) in Economics, Technical University of Lisbon."),
])
s += sec("Honours")
s += rows([
 ("2016", "Grã-Cruz (Grand Cross), Order of Prince Henry, Portuguese Republic."),
 ("2008", "European Commission Science Award (ex-Descartes Prize) for Science Communication (2nd prize); Comendador, Order of Prince Henry."),
 ("2003", "Mathematics Public Awareness First Prize, European Mathematical Society."),
])

s += sec("Books and edited volumes in education and policy")
s += pubs([
 "Crato, N. <i>O Manual Escolar</i>. Almedina, 2025.",
 "Crato, N. <i>Aprender</i>. Fundação Francisco Manuel dos Santos, 2025.",
 "Crato, N. (Ed.) <i>Developing Curriculum for Deep Thinking: The Knowledge Revival</i>. Springer, 2025.",
 "Crato, N. <i>Apología del libro de texto</i>. Narcea, 2024.",
 "Crato, N. (Ed.) <i>Improving National Education Systems After COVID-19: Moving Forward after PIRLS 2021 and PISA 2022</i>. Springer, 2024.",
 "Crato, N. (Ed.) <i>Improving a Country's Education: PISA 2018 Results in 10 Countries</i>. Springer, 2021. https://doi.org/10.1007/978-3-030-59031-4",
 "Crato, N. “Curriculum and Educational Reforms in Portugal: An Analysis on Why and How Students' Knowledge and Skills Improved”, in F. M. Reimers (Ed.), <i>Audacious Education Purposes</i>, Springer, 209–231, 2020.",
 "Crato, N. and Paruolo, P. (Eds.) <i>Data-Driven Policy Impact Evaluation: How Access to Microdata is Transforming Policy Design</i>. Springer, 2019. https://doi.org/10.1007/978-3-319-78461-8",
 "Crato, N. “A call to action for better data and better policy evaluation”, EUR 28434, Ispra, Italy, 2017. https://doi.org/10.2760/738045",
 "Behrends, E., Crato, N. and Rodrigues, J.F. (Eds.) <i>Raising Public Awareness of Mathematics</i>. Springer, 2012.",
 "Crato, N. (Ed.) <i>Ensino da Matemática: Questões e Soluções</i>. Fundação Calouste Gulbenkian, 2011.",
 "Crato, N. (Ed.) <i>Desastre no Ensino da Matemática: Como Recuperar o Tempo Perdido</i>. SPM/Gradiva, 2006.",
 "Crato, N. <i>O “Eduquês” em Discurso Directo</i>. Gradiva, 2006.",
 "Crato, N. (Coord.) <i>Rómulo de Carvalho: Ser Professor</i>. Gradiva, 2006.",
])
s += sec("Selected refereed publications")
s += pubs([
 "“Time series clustering using fragmented autocorrelations”. <i>Physica A: Statistical Mechanics and its Applications</i>, 2024.",
 "Caiado, J., Crato, N. and Poncela, P. “A fragmented-periodogram approach for clustering big data time series”. <i>Advances in Data Analysis and Classification</i>, 2019.",
 "Diniz, A., Barreiros, J. and Crato, N. “A new model for explaining long-range correlations in human time interval production”. <i>Computational Statistics &amp; Data Analysis</i> 56, 1908–19, 2012.",
 "Caiado, J., Crato, N. and Peña, D. “Tests for comparing time series of unequal lengths”. <i>J. Statistical Computation and Simulation</i> 82, 1715–1725, 2012.",
 "Crato, N., Linhares, R.R. and Lopes, S.R.C. “α-stable laws for noncoding regions in DNA sequences”. <i>J. Applied Statistics</i> 38, 261–271, 2011.",
 "Diniz, A., Barreiros, J. and Crato, N. “Parameterized estimation of long-range correlation and variance components in human serial interval production”. <i>Motor Control</i> 14, 26–43, 2010.",
 "Crato, N., Linhares, R.R. and Lopes, S.R.C. “Statistical properties of detrended fluctuation analysis”. <i>J. Statistical Computation and Simulation</i> 80, 625–641, 2010.",
 "Caiado, J. and Crato, N. “Identifying common dynamic features in stock returns”. <i>Quantitative Finance</i> 10, 797–807, 2010.",
 "Caiado, J., Crato, N. and Peña, D. “Comparison of time series with unequal length in the frequency domain”. <i>Communications in Statistics: Simulation and Computation</i> 38, 527–542, 2009.",
 "Carvalho, A., Crato, N. and Gomes, C. “A generative power-law search tree model”. <i>Computers &amp; Operations Research</i> 36, 2376–2386, 2009.",
 "Caiado, J., Crato, N. and Peña, D. “A periodogram-based metric for time series classification”. <i>Computational Statistics &amp; Data Analysis</i> 50, 2668–2684, 2006.",
 "Borges, M.F., Santos, A., Crato, N., Mendes, H. and Mota, B. “Sardine regime shifts off Portugal”. <i>Scientia Marina</i> 67-1, 235–244, 2003.",
 "Crato, N. and Ray, B.K. “Semi-parametric smoothing estimators for long-memory processes with added noise”. <i>J. Statistical Planning and Inference</i> 105, 283–297, 2002.",
 "Rammjee, R., Crato, N. and Ray, B.K. “A note on moving average forecasts of long memory processes with an application to quality control”. <i>Int. J. Forecasting</i> 18, 291–297, 2002.",
 "Costa, A.A. and Crato, N. “Long-run versus short-run behaviour of the real exchange rates”. <i>Applied Economics</i> 33, 683–688, 2001.",
 "Crato, N. and Ray, B.K. “Memory in returns and volatilities of commodity futures contracts”. <i>J. Futures Markets</i> 20, 525–544, 2000.",
 "Crato, N. “Estimation of the maximal moment exponent with censored data”. <i>Communications in Statistics: Simulation and Computation</i> 29, 1239–1254, 2000.",
 "Gomes, C.P., Selman, B., Crato, N. and Kautz, H. “Heavy-tailed phenomena in satisfiability and constraint satisfaction problems”. <i>J. Automated Reasoning</i> 24, 67–100, 2000.",
 "Breidt, J.F., Crato, N. and de Lima, P.J.F. “On the detection and estimation of long-memory in stochastic volatility”. <i>J. Econometrics</i> 83, 325–348, 1998.",
 "Crato, N. and de Lima, P.J.F. “On the power of underdifferencing and overdifferencing tests against nearly nonstationary alternatives”. <i>Communications in Statistics: Simulation and Computation</i> 26, 1431–1446, 1997.",
 "Crato, N. and Taylor, H.M. “Stationary persistent time series misspecified as nonstationary ARIMA”. <i>Statistische Hefte</i> 37, 215–223, 1996.",
 "Crato, N. and Ray, B.K. “Model selection and forecasting for long-range dependent processes”. <i>J. Forecasting</i> 15, 107–125, 1996.",
 "Crato, N. and de Lima, P. “Long-range dependence in the conditional variance of stock returns”. <i>Economics Letters</i> 45, 281–285, 1994.",
 "Crato, N. and Rothman, P. “A fractionally integration analysis of long-run behavior for U.S. macroeconomic time series”. <i>Economics Letters</i> 45, 287–291, 1994.",
])
s += sec("Other selected publications and opinion writing")
s += pubs([
 "Crato, N. “Math curriculum matters: Statistical evidence and the Portuguese experience”. <i>European Mathematical Society Magazine</i>, 2022.",
 "Crato, N. and Ruiz, E. “Can we evaluate the predictability of financial markets?”. <i>Int. J. Forecasting</i> 28, 2012.",
 "Crato, N. “Pedro Nunes, Portuguese mathematician and cosmographer”. <i>The Mathematical Intelligencer</i> 25, 2003.",
 "Crato, N. “Everything starts with the curriculum”. ResearchED 3, 2019. https://researched.org.uk/2019/02/27/everything-starts-with-the-curriculum/",
 "Crato, N. Opinion series in <i>Público</i>: “Falta educação” (2025); “Para além do PISA” (1) and (2) and “Não, nem tudo é fado” (2026).",
])
s += sec("Service to the scientific community")
s += rows([
 ("2010–", "Founding member and organiser, LESE – Lisbon Economics and Statistics of Education, a biennial international gathering of economists and statisticians dedicated to education research."),
 ("2016–2021", "Director, International Institute of Forecasters."),
 ("2011", "Guest editor, <i>International Journal of Forecasting</i>."),
 ("2000", "General Chair, 20th International Symposium on Forecasting (ISF2000); guest editor, <i>International Journal of Forecasting</i>."),
 ("1999–2001", "Board member, International Forum of Portuguese Researchers (FIIP)."),
 ("1997–2000", "Organiser, Arrábida Summer Time Series Workshops (NJIT and ISEG)."),
 ("1994", "Guest editor, <i>Managerial Finance</i>."),
])
s += sec("Education policy: Minister of Education and Science, 2011–2015")
s += [Paragraph("During this tenure, compulsory schooling was extended from nine to twelve years, English became mandatory from the third grade, the dropout rate fell from about 25% to 13.7%, retention rates improved, and Portuguese students achieved their best results to date in international surveys, including TIMSS and PISA, where 15-year-olds scored above the OECD average for the first time. Observers have highlighted more demanding standards, systematic external student evaluation, incentives based on students' progress, and wider school autonomy.", sm)]
s += sec("Teaching")
s += rows([
 ("2010–", "Professor, Department of Mathematics, ISEG."),
 ("2001–2010", "Associate Professor, ISEG."),
 ("1997–2000", "Assistant Professor, New Jersey Institute of Technology."),
 ("1992–1996", "Assistant Professor, Stevens Institute of Technology."),
 ("1992–2010", "Guest lecturer in statistics and applied time-series analysis: Victoria University of Wellington; Minas Gerais and Rio de Janeiro, Brazil; Universidad de Concepción, Chile."),
 ("1980–1988", "Earlier posts: ISEG (instructor), University of the Azores, Ponta Delgada Nursing School, Dona Leonor High School."),
])
s += sec("Scientific popularisation")
s += pubs([
 "Crato, N. and Tirapicos, L. <i>O Eclipse de Einstein</i>. CTT, 2019.",
 "Crato, N. <i>Figuring It Out: Entertaining Encounters with Everyday Math</i>. Springer, 2010.",
 "Crato, N. <i>Passeio Aleatório</i>. Gradiva, 2007 (Italian edition: <i>Passeggiata aleatoria</i>, Tropea, 2011).",
 "Crato, N., Correia de Oliveira, F. and Metello de Nápoles, S. <i>Relógios de Sol</i>. Edições CTT, 2007.",
 "Crato, N., Santos, C. and Tirapicos, L. <i>A Espiral Dourada</i>. Gradiva, 2006.",
 "Crato, N., Reis, F.E. and Tirapicos, L. <i>Trânsitos de Vénus</i>. Gradiva, 2004.",
 "<i>Zodíaco: Constelações e Mitos</i>, Gradiva, 2001; <i>Eclipses!</i>, Gradiva, 1999.",
 "Resident scientist: radio programme <i>3 minutos de Ciência</i>, Rádio Europa (2006–2009); TV programme <i>4 × Ciência</i>, RTPN (2004–2008). Science columnist, <i>Expresso</i> (1996–2011).",
])
s += sec("Languages")
s += [Paragraph("Portuguese (native); French and English (fluent); Spanish and Italian (intermediate).", sm)]

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(20*mm, 10*mm, "Nuno Crato · Curriculum Vitae · nunocrato.org"); c.drawRightString(190*mm, 10*mm, f"{d.page}"); c.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm,
                        title="Nuno Crato — Curriculum Vitae (2026)", author="Nuno Crato", invariant=1)
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
