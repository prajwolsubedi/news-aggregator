from youtube_transcript_api import YouTubeTranscriptApi


def transcribe_youtube_video(video_id: str):
    """
    Transcribe a YouTube video using youtube-transcript-api.
    Checks available transcripts and tries multiple fallback options.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        tuple: (transcript_text, error_message) or (None, error_message) if failed
    """
    try:
        print(f"   📝 Transcribing video {video_id}...")
        
        # List available transcripts for debugging
        transcript_list = None
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available = []
            for t in transcript_list:
                transcript_type = "manual" if t.is_generated == False else "auto-generated"
                available.append(f"{t.language_code} ({transcript_type})")
            print(f"   📋 Available transcripts: {', '.join(available)}")
        except Exception as e:
            print(f"   ⚠ Could not list transcripts: {e}")
        
        # Try to get transcript with multiple fallback options
        transcript = None
        
        # Option 1: Try English variants using get_transcript
        for lang_code in ['en', 'en-US', 'en-GB', 'en-AU']:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
                print(f"   ✓ Got transcript in {lang_code}")
                break
            except Exception as e:
                continue
        
        # Option 2: Use list_transcripts to fetch (handles auto-generated better)
        if not transcript and transcript_list:
            try:
                # Try manual English first
                try:
                    transcript_obj = transcript_list.find_manually_created_transcript(['en'])
                    transcript = transcript_obj.fetch()
                    print(f"   ✓ Got manual transcript in {transcript_obj.language_code}")
                except:
                    # Try auto-generated English
                    try:
                        transcript_obj = transcript_list.find_generated_transcript(['en'])
                        transcript = transcript_obj.fetch()
                        print(f"   ✓ Got auto-generated transcript in {transcript_obj.language_code}")
                    except:
                        # Try any available transcript
                        for transcript_obj in transcript_list:
                            try:
                                transcript = transcript_obj.fetch()
                                print(f"   ✓ Got transcript in {transcript_obj.language_code}")
                                break
                            except:
                                continue
            except Exception as e:
                print(f"   ⚠ Error fetching from list: {e}")
        
        if not transcript:
            raise Exception("No accessible transcripts found - transcript may be disabled or unavailable")
        
        full_text = " ".join(segment["text"] for segment in transcript)
        print(f"   ✓ Transcript retrieved ({len(full_text)} characters, {len(full_text.split())} words)")
        return full_text, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ✗ Transcription failed: {error_msg}")
        return None, error_msg
