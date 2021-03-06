# Blameful re-indenter

reindent code, whilst preserving git blame

# To use

- do one or both of:
  - run `propose_indents.py`, to generate `.proposed`-suffixed files, with the proposed indentation
  - create/modify the `.proposed`-suffixed files, with your desired indentation
    - make sure not to change the number of lines, or move lines around, or the results wont match your expectations ;-)
- run `commit_indents.py`, to write out the changes in `.proposed` files, preserving the original blame

Both scripts take as parameters a list of one or more filenames

## Single file

eg:
```
python propose_indents.py Abs.lua
python commits_indents.py Abs.lua
```

git blame before:

```
nn$ git blame Abs.lua
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  1) local Abs, parent = torc
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  2) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  3) function Abs:__init()
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  4)    parent.__init(self)
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  5) end
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  6) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  7) function Abs:updateOutpu
21eb332a (Andreas Köpf    2015-12-17 00:31:50 +0100  8)    input.THNN.Abs_update
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100  9)      input:cdata(),
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 10)      self.output:cdata()
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 11)    )
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 12)    return self.output
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 13) end
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 14) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 15) function Abs:updateGradI
21eb332a (Andreas Köpf    2015-12-17 00:31:50 +0100 16)    input.THNN.Abs_update
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 17)      input:cdata(),
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 18)      gradOutput:cdata(),
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 19)      self.gradInput:cdat
ad1efeed (Andreas Köpf    2015-12-11 23:47:10 +0100 20)    )
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 21)    return self.gradInput
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 22) end
```

git blame after:
```
nn$ git blame Abs.lua
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  1) local Abs, parent = torc
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  2) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  3) function Abs:__init()
bc7b818d (Ronan Collobert 2016-01-02 16:19:28 +0800  4)   parent.__init(self)
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  5) end
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  6) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100  7) function Abs:updateOutpu
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800  8)   input.THNN.Abs_updateO
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800  9)     input:cdata(),
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 10)     self.output:cdata()
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 11)   )
bc7b818d (Ronan Collobert 2016-01-02 16:19:28 +0800 12)   return self.output
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 13) end
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 14) 
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 15) function Abs:updateGradI
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 16)   input.THNN.Abs_updateG
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 17)     input:cdata(),
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 18)     gradOutput:cdata(),
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 19)     self.gradInput:cdata
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 20)   )
bc7b818d (Ronan Collobert 2016-01-02 16:19:28 +0800 21)   return self.gradInput
^4df3893 (Ronan Collobert 2012-01-25 14:55:20 +0100 22) end
bc7b818d (Ronan Collobert 2016-01-02 16:19:28 +0800 23) 
66ab53f4 (Andreas Köpf    2016-01-02 16:19:28 +0800 24) 
```

## Batch usage

You can pass in multiple files in one go.  They will be processed as a single batch.  One commit will be created per author, containing changes across *all* files.  This reduces the number of needed commits to be `O(A)` in number of authors, `A`, rather than `O(A*F)`, where `F` is number of files.

```
python propose_indents.py *.lua
python commits_indents.py *.lua
```
You are *strongly* recommended to check the contents of the `.proposed` files generated, prior to committing.  Determining lua indentation
is tricky, and it's hard to generate simple heuristics to handle it, without writing a full-blown lua parser, which this isn't.

# Changes

* February 22nd:
  * two phases now: first generate `.proposed` files, then commit these, with a second script, so easier to control/modify the changes
* January 3rd:
  * can now pass multiple files (eg '*.lua'), and all will be processed as one single batch

