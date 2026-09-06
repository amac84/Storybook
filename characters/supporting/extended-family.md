# Extended family (compact)

Personalities are not invented here. See `characters/family.md` for the tree.

## Grandparents

```yaml
- id: nanna
  name: Nanna
  partner: grandpa
- id: grandpa
  name: Grandpa
  partner: nanna
  distinct_from: grandpa-pete
- id: granny
  name: Granny
  partner: grandpa-pete
- id: grandpa-pete
  name: Grandpa Pete
  partner: granny
  pet:
    - id: bunny
      name: Bunny
      species: dog
      note: Lives with Granny and Grandpa Pete. Not a pet of Cove/Mars’s household.
```

## Holton and Jamie

```yaml
- id: holton
  name: Uncle Holton
  notes: Gay artistic uncle. Not a joke, lesson, or stereotype.
- id: jamie
  name: Uncle Jamie
  notes: Gay artistic uncle. Not a joke, lesson, or stereotype.
```

## The Popovicis — Andria and Andrei

Alex’s sister’s family. Stories that include them may be religious.

```yaml
- id: andria
  name: Aunty Andria
  surname: Popovici
- id: andrei
  name: Uncle Andrei
  surname: Popovici
- id: anya
  name: Anya
  gender: girl
  age: 4
  parents: [andria, andrei]
- id: adrien
  name: Adrien
  gender: boy
  age: one month younger than Mars/Eden
  parents: [andria, andrei]
- id: asher
  name: Asher
  gender: boy
  born: June 2026
  parents: [andria, andrei]
household_note: Christian family. Faith may appear when this household is in the book.
```

## Hero and Connor

```yaml
- id: hero
  name: Aunty Hero
- id: connor
  name: Uncle Connor
- id: cousin-mars
  name: Mars
  gender: girl
  age: 3 — same as protagonist Mars/Eden
  parents: [hero, connor]
  name_collision: Shares first name with protagonist Mars/Eden. Do not invent a nickname. Prefer context; brother may also be Eden.
notes: See hero.md.
```

## Hayley and Nate

```yaml
- id: hayley
  name: Aunty Hayley
- id: nate
  name: Uncle Nate
- id: archer
  name: Archer
  gender: boy
  age: 13
  parents: [hayley, nate]
- id: ashton
  name: Ashton
  gender: boy
  age: 10
  parents: [hayley, nate]
- id: arlo
  name: Arlo
  gender: boy
  age: 7
  parents: [hayley, nate]
pets:
  - two cats (names not locked — do not invent)
  note: Live with Hayley and Nate. Not pets of Cove/Mars’s household.
```
