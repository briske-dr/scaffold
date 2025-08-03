from etl.extractor import OverpassQuarryExtractor
from etl.pipeline import ETLPipeline

extractor = OverpassQuarryExtractor("Italia")
pipeline = ETLPipeline(extractor)
pipeline.run("italia_pedreiras_limpo.geojson")
