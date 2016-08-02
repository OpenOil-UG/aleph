from setuptools import setup, find_packages

setup(
    name='aleph',
    version='1.0',
    description="Document sifting web frontend",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://grano.cc',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    test_suite='nose.collector',
    entry_points={
        'aleph.ingestors': [
            'skip = aleph.ingest.dummy:SkipIngestor',
            'pdf = aleph.ingest.text:PDFIngestor',
            'doc = aleph.ingest.document:DocumentIngestor',
            'ppt = aleph.ingest.document:PresentationIngestor',
            'html = aleph.ingest.html:HtmlIngestor',
            'img = aleph.ingest.image:ImageIngestor',
            'email = aleph.ingest.email:EmailFileIngestor',
            'pst = aleph.ingest.email:OutlookIngestor',
            'messy = aleph.ingest.tabular:MessyTablesIngestor',
            'dbf = aleph.ingest.dbf:DBFIngestor',
            'rar = aleph.ingest.packages:RARIngestor',
            'zip = aleph.ingest.packages:ZipIngestor',
            'tar = aleph.ingest.packages:TarIngestor',
            'gz = aleph.ingest.packages:GzipIngestor',
            'bz2 = aleph.ingest.packages:BZ2Ingestor'
        ],
        'aleph.analyzers': [
            'lang = aleph.analyze.language:LanguageAnalyzer',
            'emails = aleph.analyze.regex:EMailAnalyzer',
            'urls = aleph.analyze.regex:URLAnalyzer',
            'regex = aleph.analyze.regex_entity:RegexEntityAnalyzer',
            #'polyglot = aleph.analyze.polyglot_entity:PolyglotEntityAnalyzer'
        ],
        'aleph.crawlers': [
            # 'stub = aleph.crawlers.stub:StubCrawler',
            #'opennames = aleph.crawlers.opennames:OpenNamesCrawler',
            #'idrequests = aleph.crawlers.idashboard:IDRequests',
            #'idfiles = aleph.crawlers.idashboard:IDFiles',
            #'blacklight = aleph.crawlers.blacklight:BlacklightCrawler',
            #'sourceafrica = aleph.crawlers.documentcloud:SourceAfricaCrawler',
            #'sample = aleph_openoil.crawlers.sample:SampleCrawler',
            'asx = aleph_openoil.crawlers.asx:ASXCrawler',
            'edgar = aleph_openoil.crawlers.edgar:EdgarCrawler',
            'bombay = aleph_openoil.crawlers.bombay:BombayCrawler',
            'johannesburg = aleph_openoil.crawlers.south_africa:JohannesburgCrawler',
            'oocontracts = aleph_openoil.crawlers.oocontracts:OpenOilContractsCrawler',
            'sedar = aleph_openoil.crawlers.sedar:SedarCrawler',
            'singapore = aleph_openoil.crawlers.singapore:SingaporeCrawler',
            'edgar_html = aleph_openoil.crawlers.edgar:EdgarHTMLCrawler', 
            'eiti = aleph_openoil.crawlers.sedar:EITICrawler',
        ],
        'aleph.init': [
        ],
        'console_scripts': [
            'aleph = aleph.manage:main',
        ]
    },
    tests_require=[
        'coverage', 'nose'
    ]
)
