import json
import pandas as pd
import os

def clean_and_convert(interactions_path, meta_path, out_interactions, out_meta):
    print("Bước 1: Quét file metadata để lọc ra các tựa game hợp lệ...")
    valid_items = {}
    
    # Các từ khóa nhận diện phụ kiện (cần loại bỏ) để tránh Data Leakage
    accessory_keywords = [
        'protector', 'mouse', 'headset', 'cable', 'controller', 'case', 
        'charger', 'battery', 'stand', 'keyboard', 'adapter', 'thumb grip', 
        'skin', 'cover', 'glass', 'thumbstick'
    ]
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                title = record.get('title', '').strip()
                
                # Bỏ qua nếu không có title (để tránh lỗi "Không rõ")
                if not title:
                    continue
                
                # Bỏ qua nếu title chứa các từ khóa phụ kiện
                title_lower = title.lower()
                is_accessory = any(kw in title_lower for kw in accessory_keywords)
                if is_accessory:
                    continue
                
                # Chỉ lấy danh mục 'Video Games' nếu field này tồn tại
                main_category = record.get('main_category', '')
                if main_category and main_category != 'Video Games':
                    continue
                
                record_id = record.get('parent_asin') or record.get('asin')
                if record_id:
                    valid_items[record_id] = record
                    
            except json.JSONDecodeError:
                continue
                
    print(f"Tìm thấy {len(valid_items)} tựa game hợp lệ (có title, không phải phụ kiện).")
    
    print("Bước 2: Lọc file interactions dựa trên danh sách game hợp lệ...")
    chunk_size = 100000
    first_chunk = True
    total_interactions = 0
    valid_item_ids_found = set()
    
    reader = pd.read_json(interactions_path, lines=True, chunksize=chunk_size)
    for i, chunk in enumerate(reader):
        # Giữ lại những interaction thuộc về valid_items
        if 'parent_asin' in chunk.columns:
            mask = chunk['parent_asin'].isin(valid_items.keys())
        elif 'asin' in chunk.columns:
            mask = chunk['asin'].isin(valid_items.keys())
        else:
            mask = [False] * len(chunk)
            
        filtered_chunk = chunk[mask]
        
        if len(filtered_chunk) > 0:
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            filtered_chunk.to_csv(out_interactions, mode=mode, header=header, index=False, encoding='utf-8')
            first_chunk = False
            total_interactions += len(filtered_chunk)
            
            # Ghi nhận các item thực sự có interaction
            if 'parent_asin' in filtered_chunk.columns:
                valid_item_ids_found.update(filtered_chunk['parent_asin'].dropna().unique())
            elif 'asin' in filtered_chunk.columns:
                valid_item_ids_found.update(filtered_chunk['asin'].dropna().unique())
                
        if (i + 1) % 5 == 0:
            print(f"  Đã quét {i * chunk_size} interactions...")
                
    print(f"Đã lưu {total_interactions} interactions hợp lệ vào {out_interactions}")
    
    print("Bước 3: Lưu metadata của các game có interaction...")
    # Chỉ lưu metadata của những item có interaction
    final_meta = [valid_items[iid] for iid in valid_item_ids_found if iid in valid_items]
    
    df_meta = pd.DataFrame(final_meta)
    df_meta.to_csv(out_meta, index=False, encoding='utf-8')
    
    print(f"Đã lưu {len(df_meta)} metadata lines vào {out_meta}")
    print("\nHoàn tất quá trình làm sạch dữ liệu (Data Cleaning)!")

if __name__ == "__main__":
    base_dir = "data"
    interactions_file = os.path.join(base_dir, "Video_Games.jsonl")
    meta_file = os.path.join(base_dir, "meta_Video_Games.jsonl")
    
    out_interactions = os.path.join(base_dir, "Video_Games.csv")
    out_meta = os.path.join(base_dir, "meta_Video_Games.csv")
    
    if os.path.exists(interactions_file) and os.path.exists(meta_file):
        clean_and_convert(interactions_file, meta_file, out_interactions, out_meta)
    else:
        print("Không tìm thấy file JSONL trong thư mục data/. Hãy kiểm tra lại đường dẫn.")

