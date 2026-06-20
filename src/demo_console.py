import os
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Thêm đường dẫn để import được từ thư mục cha
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.DataIO import DataIO
from utils.Timer import Timer
from core.Recommender import Recommender

console = Console()

def print_header():
    console.print(Panel.fit(
        "[bold cyan]HỆ THỐNG GỢI Ý TRÒ CHƠI / SẢN PHẨM[/bold cyan]\n[green]Đồ án Cấu trúc dữ liệu và Giải thuật[/green]\n[dim]Sử dụng thuật toán LSH/MinHash[/dim]", 
        border_style="cyan"
    ))

def load_and_build_system():
    # Sử dụng tập dữ liệu 10k (Hoàn hảo nhất cho demo)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    review_file = os.path.join(base_dir, 'data', 'Video_Games_10k.csv')
    meta_file = os.path.join(base_dir, 'data', 'meta_Video_Games_10k.csv')
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="[cyan]Đang tải dữ liệu từ DataIO...", total=None)
        
        # 1. Load Data
        data_io = DataIO(review_file, meta_file)
        # Giảm min_interactions xuống 2 cho tập dữ liệu 10k để không bị lọc quá đà
        # Nếu dùng tập filtered (1GB) thì có thể tăng lên 3 hoặc 5
        data_io.load_data(min_interactions=2) 
        
        user_index = data_io.get_user_index()
        item_index = data_io.get_item_index()
        
        progress.update(task, description="[cyan]Đang khởi tạo thuật toán LSH (Hash & Band)...")
        
        # 2. Build Recommender
        recommender = Recommender(
            user_index, 
            item_index,
            num_hashes=100,
            num_bands=50,
            rows_per_band=2
        )
        
    console.print(f"[bold green]✔[/bold green] Đã nạp thành công [yellow]{len(user_index)}[/yellow] Users và [yellow]{len(item_index)}[/yellow] Items!")
    return recommender, item_index

def display_recommendations(user_id, recommendations, item_index, latency):
    if not recommendations:
        console.print("[yellow]Không tìm thấy gợi ý nào. Người dùng này có thể không đủ dữ liệu hoặc là Cold Start![/yellow]")
        return
        
    table = Table(title=f"Danh sách gợi ý cho User ID: [yellow]{user_id}[/yellow]")
    table.add_column("Top", justify="center", style="cyan", no_wrap=True)
    table.add_column("Mã ASIN", style="blue")
    table.add_column("Tên Sản phẩm / Game", style="magenta")
    table.add_column("Độ tương đồng", justify="right", style="green")

    for idx, (asin, score) in enumerate(recommendations, 1):
        # Truy xuất tên game từ item_index (giống file main.py của bạn)
        title = "Không rõ"
        if asin in item_index:
            item = item_index[asin]
            title = item.title if item.title else "Không rõ"
            
        # Cắt ngắn title nếu quá dài để bảng không bị bể
        if len(title) > 40:
            title = title[:37] + "..."
            
        table.add_row(str(idx), asin, title, f"{score:.4f}")

    console.print(table)
    console.print(f"\n⏱️  [bold]Thời gian truy xuất (Latency):[/bold] [yellow]{latency:.4f} giây[/yellow]")
    console.print(f"🎯 [bold]Độ phức tạp thuật toán:[/bold] [blue]O(1)[/blue] hoặc [blue]O(K)[/blue] (Nhờ LSH)\n")

def main():
    # 1. In tiêu đề
    print_header()
    
    # 2. Khởi tạo dữ liệu THẬT
    try:
        recommender, item_index = load_and_build_system()
    except Exception as e:
        console.print(f"[bold red]Lỗi khởi tạo hệ thống: {e}[/bold red]")
        return
        
    # In ra một số User ID có trong hệ thống để test cho dễ copy paste
    sample_users = list(recommender.user_index.keys())[:5]
    console.print(f"\n[dim]💡 Một số ID để bạn copy test thử: {', '.join(sample_users)}[/dim]")
    
    # 3. Vòng lặp chính
    while True:
        console.print("[bold]Nhập User ID để lấy gợi ý (hoặc gõ 'q' để thoát):[/bold] ", end="")
        user_input = input().strip()
        
        if user_input.lower() == 'q':
            console.print("[bold red]Đã thoát chương trình. Cảm ơn bạn![/bold red]")
            break
            
        if not user_input:
            continue
            
        console.print("\n[dim]Đang chạy thuật toán LSH...[/dim]")
        
        # Đo thời gian bằng Timer (như file Timer.py của bạn nhưng viết inline cho gọn)
        start_time = time.time()
        
        try:
            # Lấy 10 gợi ý từ class Recommender thật của bạn
            recommendations = recommender.recommend(user_input, top_k=10)
            latency = time.time() - start_time
            
            # Hiển thị
            display_recommendations(user_input, recommendations, item_index, latency)
        except Exception as e:
            console.print(f"[bold red]Có lỗi xảy ra trong lúc tính toán: {e}[/bold red]")
            
        console.print("-" * 70)

if __name__ == "__main__":
    main()
