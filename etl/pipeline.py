class ETLPipeline:
    def __init__(self, extractor):
        self.extractor = extractor
        self.gdf = None

    def extract(self):
        print("🔍 Extraindo dados...")
        self.gdf = self.extractor.run()

    def transform(self):
        print("🛠️ Transformando dados...")
        gdf = self.gdf.copy()

        # Filtra apenas colunas relevantes
        columns_to_keep = ['geometry', 'landuse', 'operator',         'name']
        existing_cols = [col for col in columns_to_keep if col in gdf.columns]
        gdf = gdf[existing_cols]

        # Adiciona coluna padronizada de tipo
        def infer_tipo(row):
            if row.get('landuse') == 'quarry':
                return 'quarry'
            elif row.get('industrial') == 'mine':
                return 'mine'
            elif row.get('man_made') == 'tailings_pond':
                return 'tailings_dam'
            return 'desconhecido'

        gdf['tipo'] = gdf.apply(infer_tipo, axis=1)

        # Substitui NaNs por valores default
        gdf['name'] = gdf.get('name', None).fillna("Sem nome")

        self.gdf = gdf

    def load(self, output_path):
        print(f"💾 Salvando dados transformados em: {output_path}")
        self.gdf.to_file(output_path, driver="GeoJSON")

    def run(self, output_path):
        self.extract()
        self.transform()
        self.load(output_path)
        print(
            f"🏁 ETL finalizado com sucesso. Total de feições: {len(self.gdf)}")
