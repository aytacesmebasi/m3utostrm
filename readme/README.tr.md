README.tr.md

Bu proje, chatgpt, iptv-org ve tmdb apilerinin öğrenilmesi amacıyla hazırlanmıştır. Kodları tamamen chatgpt yazmıştır, bu nedenle ne eksik, ne fazla veya ne yanlış bilmiyorum. İleride herhangi bir isteğinizle ilgili düzenleme yapabilir miyim bilmiyorum.

IPTV servis sağlayıcılarından indirilen '.m3u' dosyalarının içeriklerini taramak ve filmler ve TV şovları için '.strm' dosyaları oluşturmak için Python kullanır. Ayrıca TMDB API'sini kullanarak '.nfo' dosyaları oluşturur ve IPTVORG API'siyle TV yayınlarını '.m3u' dosyalarında düzenler.

Uygulama bu işlemleri yapmak için şu yolu izler;
1) Kullanılacak olan python kütüphaneleri eğer yüklü değilse yükler,

2) Kullanıcının verdiği iptv sağlayıcı bilgileri ile '.m3u' dosyasını uygulamanın çalıştırıldığı tarih ve saate uygun olarak isim vererek indirir,

3) İndirilen '.m3u' dosyasının bulunduğu klasörde başka '.m3u' dosyaları eğer yoksa ayrıca 'tobeprocess.m3u' dosyası olarak kaydeder,

4) İndirilen '.m3u' dosyasının bulunduğu klasörde başka '.m3u' dosyaları varsa isimlerine bakarak en güncelini bulur, 

5) Bulduğu en güncel '.m3u' dosyasında bulunmayan ancak yeni indirilen '.m3u' dosyasında bulunan url satırlarını 'tobeprocess.m3u' dosyası olarak kaydeder,

6) 'tobeprocess.m3u' dosyasındaki url'leri sayarak kalan işlem sayısının takibini sağlar,

7) '.strm' ve '.nfo' dosyalarını kaydetmek üzere filmler için 'movies', diziler için 'series' ve porno içerikler için 'porn' klasörlerini oluşturur,

8) Kodda bulunan suffix pattern ile iptv kanal yayınlarının isimlerini düzenler,

9) İsimlendirilmesi porno isimlendirmeye uygun olan 'url' ler için 'porn' klasöründe '.strm' dosyaları oluşturur,

10) Tmdb api anahtarını kullanarak geri kalan 'url' leri film ve dizi olarak ayırır,

11) Filmleri 'movies' klasörü içinde her film için kendi adıyla klasör oluşturur ve bu klasör içine filmin 'url' sinin yazılı olduğu '.strm' dosyası ile tmdb sitesinden alınan bilgilerin bulunduğu '.nfo' dosyasını oluşturur,

12) Dizileri 'series' klasörü içinde her dizi için kendi adıyla klasör oluşturur,  bu klasör sezonlar için de klasör oluşturur ve içine dizi 'url' sinin yazılı olduğu '.strm' dosyası ile tmdb sitesinden alınan bilgilerin bulunduğu '.nfo' dosyasını oluşturur,

13) İndirilen '.m3u' dosyasında iptv kanal yayınları için yeni bir 'updated_channels.m3u' isimli bir dosya oluşturur ve içeriğini iptv-org apisi ile düzenler,


Yapılması düşünülen geliştirmeler;
- '.m3u' dosyasını indirme veya varolan dosyayı işleme seçeneği.
