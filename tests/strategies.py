#   Copyright 2021 Modelyst LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from string import printable

from hypothesis import strategies as st

from .examples import Address, Book, BookWithPrice, Person

book_strat = st.builds(Book)

basic_strats = {
    Book: st.builds(Book),
    Person: st.builds(Person),
    Address: st.builds(Address),
    BookWithPrice: st.builds(BookWithPrice),
}

python_simples = st.one_of(
    st.none(), st.booleans(), st.integers(), st.text(printable), st.floats()
)


@st.composite
def json_strat(draw, allow_base_outputs: bool = True, max_leaves=4):
    if not allow_base_outputs:
        base = st.lists(python_simples) | st.dictionaries(
            st.text(printable), python_simples
        )
    else:
        base = python_simples
    json_data = draw(
        st.recursive(
            base,
            lambda children: st.lists(children)
            | st.dictionaries(st.text(printable), children),
            max_leaves=max_leaves,
        )
    )
    return json_data
