{
    "Accept": [
        "q3"
    ],
    "Alphabet": [
        "a",
        "b"
    ],
	"TapeAlphabet": [
	    "Б",
        "a",
        "b"
    ],
    "D-Table": {
        "q0": {
            "Б": "q1, Б, →"
        },
        "q1": {
            "a": "q2, a, →",
            "b": "q1, b, →"
        },
        "q2": {
            "a": "q3, a, →",
            "b": "q1, b, →"
        }
    },
    "Start": "q0",
    "States": [
        "q0",
        "q1",
        "q2",
        "q3"
    ]
}