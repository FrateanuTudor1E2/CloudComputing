import http.server
import socketserver
import urllib.parse
import json
import xml.etree.ElementTree as ET

class BookListResource(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query

        if query:
            book_id = urllib.parse.parse_qs(query)['id'][0]
            response = self.get_book(book_id)
        else:
            response = self.get_books()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        book_data = json.loads(post_data)

        book_id = self.add_book(book_data)

        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.send_header('Location', '/books?id=' + str(book_id))
        self.end_headers()

        response = {'message': 'Book created'}
        self.wfile.write(json.dumps(response).encode())

    def do_PUT(self):
        query = urllib.parse.urlparse(self.path).query
        query_params = urllib.parse.parse_qs(query)

        if 'id' not in query_params:
            self.send_error(400, 'Missing required parameter: id')
            return

        book_id = query_params['id'][0]

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        book_data = json.loads(post_data)

        self.update_book(book_id, book_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {'message': 'Book updated'}
        self.wfile.write(json.dumps(response).encode())
    def do_DELETE(self):
        query = urllib.parse.urlparse(self.path).query
        book_id = urllib.parse.parse_qs(query)['id'][0]

        self.delete_book(book_id)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {'message': 'Book deleted'}
        self.wfile.write(json.dumps(response).encode())

    def get_books(self):
        tree = ET.parse('books.xml')
        root = tree.getroot()

        books = []
        for book in root.findall('book'):
            book_dict = {}
            book_dict['id'] = book.get('id')
            book_dict['title'] = book.find('title').text
            book_dict['author'] = book.find('author').text
            book_dict['year'] = book.find('year').text
            books.append(book_dict)

        return {'books': books}

    def get_book(self, book_id):
        tree = ET.parse('books.xml')
        root = tree.getroot()

        for book in root.findall('book'):
            if book.get('id') == book_id:
                book_dict = {}
                book_dict['id'] = book_id
                book_dict['title'] = book.find('title').text
                book_dict['author'] = book.find('author').text
                book_dict['year'] = book.find('year').text
                return {'book': book_dict}

        return {'message': 'Book not found'}

    def add_book(self, book_data):
        tree = ET.parse('books.xml')
        root = tree.getroot()

        book = ET.Element('book', id=str(len(root) + 1))
        ET.SubElement(book, 'title').text = book_data['title']
        ET.SubElement(book, 'author').text = book_data['author']
        ET.SubElement(book, 'year').text = book_data['year']
        root.append(book)
        tree.write('books.xml')
        return str(len(root))

    def update_book(self, book_id, book_data):
        print("book_id:", book_id)
        print("book_data:", book_data)

        tree = ET.parse('books.xml')
        root = tree.getroot()
        book_elem = root.find(f"./book[@id='{book_id}']")

        book_elem.find('title').text = book_data['title']
        book_elem.find('author').text = book_data['author']
        book_elem.find('year').text = book_data['year']

        tree.write('books.xml')

        return {'message': 'Book updated'}

    def delete_book(self, book_id):
        tree = ET.parse('books.xml')
        root = tree.getroot()

        for book in root.findall('book'):
            if book.get('id') == book_id:
                root.remove(book)
                tree.write('books.xml')
                return

if __name__ == '__main__':
        PORT = 8000
        handler = BookListResource
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()