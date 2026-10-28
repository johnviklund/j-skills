# Pictures

   - **Pictures question:** when step 3 needs a capture and the app cannot run here (missing
     data, credentials or dependencies), ask in the same message as the video question,
     lettered d to f: d) the human captures them, with each screen listed by route, state and
     the 1280×800 viewport, and the folder to drop JPEGs in; e) a render of the real UI
     components with made-up data, step 3.4; f) *not captured* boxes. Recommend d when a screen
     only makes sense with real data, e otherwise. With no human to ask, e when the UI can be
     exported, else f.

3. **Pictures.** Done when every screen the page shows has its picture, a before and an after
   for a slug's changed screen and one for an area's screen, or a stated reason for each one
   missing. Skip this step when the page shows no screen. Take the cheapest source that exists:
   1. The run's own `screens/` (execute saves them per UI ticket): use them as they are.
   2. The repo's verify skill (`verify-<app>`, made by `verify.create`): its control CLI starts
      the app and saves a screenshot of a route, with the same data every time.
   3. Capture with a browser tool. *After*: run the app at `HEAD`. *Before*: a worktree at the
      plan's `Base` (`git worktree add $TMPDIR/understand-before <Base>`; reuse the main
      checkout's dependencies when the lockfile is unchanged; another port). Same route, viewport
      1280×800 and data for both; crop to the changed region; JPEG into the output folder's
      `screens/`. Remove the worktree after.
   4. The app cannot run here: follow the answer to step 2's pictures question.
      - **d, the human captures:** go on with steps 4 and 5 while they do, and place the files
        when they arrive; a screen still missing at step 6 gets a *not captured* box.
      - **e, made-up data:** export the UI with `git archive HEAD <ui folder> | tar -x -C
        $TMPDIR/understand-ui`, so the target checkout stays untouched, and install its
        dependencies there. Add one page that renders the real components with data shaped
        like the repo's own test fixtures, and screenshot each state at 1280×800. Where the
        backend builds what a component shows, such as chart values, run that backend code on
        the made-up data instead of writing the values by hand. The page says the data is made
        up, in the section's opening line and in no customer's words.
      - **f:** a *not captured* box, with the reason in the caption.

   Open each picture at most once, to write its caption.
