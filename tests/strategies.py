from hypothesis import strategies as st
from .examples import Book, BookWithPrice, Person, Address

book_strat = st.builds(Book)

basic_strats = {
    Book: st.builds(Book),
    Person: st.builds(Person),
    Address: st.builds(Address),
    BookWithPrice: st.builds(BookWithPrice),
}
