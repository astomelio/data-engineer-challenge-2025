#!/usr/bin/env python3
"""
Script simple para ver estadísticas rápidas de los datos
"""

import pandas as pd
from pathlib import Path

def show_stats():
    """Muestra estadísticas básicas de los datos"""
    
    # Buscar archivos Excel en la carpeta data/
    data_dir = Path("data")
    excel_files = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
    
    if not excel_files:
        print("❌ No se encontraron archivos Excel en la carpeta 'data/'")
        return
    
    print("✅ Archivos Excel encontrados:")
    for file in excel_files:
        print(f"  - {file.name}")
    
    print("\n📊 ESTADÍSTICAS RÁPIDAS:")
    print("=" * 40)
    
    # Procesar cada archivo Excel
    total_records = 0
    for excel_file in excel_files:
        try:
            print(f"\n📄 Procesando: {excel_file.name}")
            df = pd.read_excel(excel_file)
            
            print(f"  Filas: {len(df):,}")
            print(f"  Columnas: {len(df.columns)}")
            print(f"  Columnas: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            
            # Mostrar algunos datos de ejemplo
            print(f"  Ejemplo de datos:")
            for i, row in df.head(2).iterrows():
                print(f"    Fila {i+1}: {dict(row.head(3))}")
            
            total_records += len(df)
            
        except Exception as e:
            print(f"  ❌ Error leyendo {excel_file.name}: {e}")
    
    print(f"\n📈 TOTAL: {total_records:,} registros en todos los archivos")
    print("\n✅ Listo!")

if __name__ == "__main__":
    show_stats()
