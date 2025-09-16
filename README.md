# College Timetable Generator

This is a Python application that generates optimized weekly timetables for college classes using Google OR-Tools.

## Features

- Generates timetables for two divisions (TY_A and TY_B)
- Handles both theory and practical sessions
- Enforces all specified constraints:
  - Mutual exclusion (if Div A has practical, Div B must have theory)
  - Teacher break constraints (no consecutive lectures)
  - Lab capacity constraints
  - Practical batch requirements (P, Q, R groups)
- Exports timetables to JSON format

## Requirements

- Python 3.6+
- Google OR-Tools

## Installation

1. Install the required dependencies:
   ```
   pip install ortools
   ```

## Usage

1. Run the timetable generator:
   ```
   python new_timetable_generator.py
   ```

2. Follow the interactive prompts to enter:
   - Lab information
   - Subjects with theory and practical requirements
   - Teacher information and subject assignments

3. Review the input summary and confirm generation

4. View the generated timetable in grid format

5. Optionally export the timetable to JSON format

## Example Input

When running the program, you'll be prompted to enter:

1. **Labs**: Number and names of available practical labs
2. **Subjects**: 
   - Subject names
   - Required theory hours per week
   - Required practical hours per week
   - Preferred labs for practical sessions
3. **Teachers**:
   - Teacher IDs and names
   - Subjects each teacher can teach
4. **Confirm**: Review all input data before generation

## Output

The timetable will be displayed in a grid format showing:
- Days of the week
- Time slots (10:30-11:30, 11:30-12:30, 12:30-1:30, 2:00-3:00, 3:00-4:00, 4:00-5:00, 5:00-6:00)
- Activities for each division (theory/practical sessions)
- Teacher assignments
- Lab assignments for practical sessions
- Batch information for practical sessions

## Constraints Satisfied

- Each subject has both theory and practical components
- When Division A has a practical, Division B has a theory session (and vice versa)
- Teachers don't have consecutive lectures
- Practical sessions include all 3 batches (P, Q, R)
- Lab capacity constraints are respected
- Minimum lecture requirements are met

## Files

- `new_timetable_generator.py`: Main application
- `FINAL_SUMMARY.md`: Detailed implementation summary
- Various test files for verification

## Troubleshooting

If the timetable generator reports that it cannot generate a valid timetable:
1. Check that lecture requirements don't exceed available time slots
2. Ensure sufficient labs are available for practical sessions
3. Verify teacher assignments are realistic
4. Consider reducing lecture requirements or adding more time slots