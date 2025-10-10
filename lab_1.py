import pandas as pd
import random
import multiprocessing
from multiprocessing import Pool   

def gen_files(n=5, rows=10):
    for i in range(n):
        data = []
        for j in range(rows):
            data.append([random.choice(['A', 'B', 'C', 'D']), random.uniform(0.0, 999.9)])
        
        df = pd.DataFrame(data, columns=['Категория', 'Значение'])
        df.to_csv(f"file{i}.csv", index=False)

def process_file(filename):
    df = pd.read_csv(filename)
    group = df.groupby('Категория')['Значение'].agg(['median', 'std'])
    return group

if __name__ == '__main__':
    gen_files()
    
    files = [f"file{i}.csv" for i in range(5)]
    
    with Pool() as executor:
        results = executor.map(process_file, files)

    all_results = list(results)
    
    for result in all_results:
        print(result)
    
    combined_results = pd.concat(all_results, axis=0)    
    combined_results = combined_results.drop(columns=['std'])
    
    # print(combined_results)
    
    aggregated = combined_results.groupby(combined_results.index)['median'].agg(['median', 'std'])

    print("\nИтог:\n",aggregated)