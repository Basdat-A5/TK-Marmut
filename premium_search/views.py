from django.shortcuts import render, redirect
from django.db import connection
import psycopg2, os
from psycopg2 import Error
import uuid
from datetime import datetime, timedelta
from django.http import JsonResponse

def riwayat(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    email = request.COOKIES.get('email') 

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("SET SEARCH_PATH TO A5")
            cursor.execute("SELECT * FROM TRANSACTION WHERE email = %s ORDER BY timestamp_dimulai DESC;", [email])
            rows = cursor.fetchall()
            transactions = [
                {
                    'id': row[0],
                    'jenis_paket': row[1],
                    'email': row[2],
                    'timestamp_dimulai': row[3],
                    'timestamp_berakhir': row[4],
                    'metode_bayar': row[5],
                    'nominal': row[6]
                }
                for row in rows
            ]
        connection.commit()
        cursor.close()
        connection.close()
        return render(request, 'riwayat.html', {'transactions': transactions})

def cek_langganan(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    if request.method == 'POST':
        data = request.POST
        email = request.COOKIES.get('email') 
        jenis_paket = data.get('jenis_paket')
        metode_bayar = data.get('metode_bayar')
        
        package_durations = {
            '1 bulan': 1,
            '3 bulan': 3,
            '6 bulan': 6,
            '1 tahun': 12
        }

        duration = package_durations[jenis_paket]
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration * 30) 
        transaction_id = str(uuid.uuid4())

        with connection.cursor() as cursor:
            cursor.execute("SELECT harga FROM PAKET WHERE jenis = %s;", [jenis_paket])
            result = cursor.fetchone()
            if result:
                nominal = result[0]
            else:
                connection.commit()
                cursor.close()
                connection.close()
                return render(request, 'cek_langganan.html', {'error': 'Package type not found'})

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TRANSACTION (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, [transaction_id, jenis_paket, email, start_date, end_date, metode_bayar, nominal])
            

            cursor.execute("SELECT * FROM PREMIUM WHERE email = %s;", [email])
            result = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return render(request, 'cek_langganan.html')


def payment(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    jenis_paket = request.GET.get('jenis_paket')
    harga = request.GET.get('harga')
    connection.commit()
    cursor.close()
    connection.close()
    return render(request, 'payment.html', {'jenis_paket': jenis_paket, 'harga': harga})

def process_payment(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    if request.method == 'POST':
        email = request.COOKIES.get('email')  
        jenis_paket = request.POST.get('jenis_paket').strip()
        harga = request.POST.get('harga').strip()
        metode_bayar = request.POST.get('metode_bayar').strip()
        
        try:
            
            package_durations = {
                '1 bulan': 1,
                '3 bulan': 3,
                '6 bulan': 6,
                '1 tahun': 12
            }

            duration = package_durations[jenis_paket]
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration * 30)

            transaction_id = str(uuid.uuid4())

            with connection.cursor() as cursor:
                cursor.execute("SET SEARCH_PATH TO A5")
                
                cursor.execute("""
                    INSERT INTO TRANSACTION (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, [transaction_id, jenis_paket, email, start_date, end_date, metode_bayar, harga])
                    
                connection.commit()
                    
            connection.commit()
            cursor.close()
            connection.close()
            response = redirect('dashboard:dashboard')
            response.set_cookie('statusLangganan', 'Premium')
            return response

        except Exception as e:
            print(f"Error: {e}")
            return render(request, 'already_subscribed.html')
            

def downloaded_song(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    email = request.COOKIES.get('email')

    with connection.cursor() as cursor:
        cursor.execute("SET SEARCH_PATH TO A5")
        cursor.execute("""
            SELECT k.judul, ak.nama, ds.id_song
            FROM DOWNLOADED_SONG ds
            JOIN SONG s ON ds.id_song = s.id_konten
            JOIN KONTEN k ON s.id_konten = k.id
            JOIN ARTIST a ON s.id_artist = a.id
            JOIN AKUN ak ON a.email_akun = ak.email
            WHERE ds.email_downloader = %s
        """, [email])
        rows = cursor.fetchall()
        songs = [
            {
                'id_song': row[2],
                'judul': row[0],
                'nama_artist': row[1],
            }
            for row in rows
        ]
    connection.commit()
    cursor.close()
    connection.close()
    return render(request, 'downloaded_song.html', {'songs': songs})

def delete(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    email = request.COOKIES.get('email')
    id_song = request.GET.get('id_song')

    with connection.cursor() as cursor:
        cursor.execute("SET SEARCH_PATH TO A5")
        cursor.execute("""
            DELETE FROM DOWNLOADED_SONG
            WHERE id_song = %s AND email_downloader = %s
        """, [id_song, email])
    connection.commit()
    cursor.close()
    connection.close()
    return JsonResponse({'message': 'Song deleted successfully', 'id_song': id_song})


def search_bar(request):
    # Connect ke db
    connection = psycopg2.connect(user='postgres.coxvdmwovhpyalowubwg',
                                  password='basdatbagus',
                                  host='aws-0-ap-southeast-1.pooler.supabase.com',
                                  port=5432,
                                  database='postgres')

    # Buat cursor buat operasiin db
    cursor = connection.cursor()

    # Masuk ke schema A5
    cursor.execute("SET search_path TO A5")
    query = request.GET.get('query', '').lower()  
    if not query:
        #Jika search bar kosong
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    
    results = []
    with connection.cursor() as cursor:

        cursor.execute("SET SEARCH_PATH TO A5")
        
        cursor.execute("""
            SELECT 'PODCAST' AS type,
            k.judul AS judul,
            a.nama AS oleh,
            k.id AS id
            FROM podcast p
            JOIN konten k ON p.id_konten = k.id
            JOIN podcaster pod ON p.email_podcaster = pod.email
            JOIN akun a ON pod.email = a.email
            WHERE LOWER(k.judul) LIKE %s
        """, [f"%{query}%"])
        results.extend(cursor.fetchall())

        
        cursor.execute("""
            SELECT 'SONG' AS type,
            k.judul AS judul,
            a.nama AS oleh,
            k.id AS id
            FROM song s
            JOIN konten k ON s.id_konten = k.id
            JOIN artist ar ON s.id_artist = ar.id
            JOIN akun a ON ar.email_akun = a.email
            WHERE LOWER(k.judul) LIKE %s
        """, [f"%{query}%"])
        results.extend(cursor.fetchall())

       
        cursor.execute("""
            SELECT 'USER PLAYLIST' AS type,
            up.judul AS judul,
            a.nama AS oleh,
            up.id_user_playlist  AS id       
            FROM user_playlist up
            JOIN akun a ON up.email_pembuat = a.email
            WHERE LOWER(up.judul) LIKE %s
        """, [f"%{query}%"])
        results.extend(cursor.fetchall())

    context = {
        'query': query,
        'results': [{
            'type': result[0],
            'title': result[1],
            'by': result[2],
            'id' : result[3],
        } for result in results]
    }
    connection.commit()
    cursor.close()
    connection.close()
    return render(request, 'search.html', context)